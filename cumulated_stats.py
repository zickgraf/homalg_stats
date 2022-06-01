#!/usr/bin/env python3

import datetime
import os
import re
import subprocess

start_date = datetime.datetime(2000, 1, 1)
start_unix = datetime.datetime.timestamp(start_date)


# list of known large commits
large_commit_hash_whitelist = [
	# homalg_project
	"196077343639b5aec6b0296ccb61c83d3d009f29",
	"f75b4964a6690075303120b52c10e885a66f161c",
	"265addea76eb9bcf7c593e08d9ef64596f6120de",

	# CAP_project
	"f4297869ede8b845cd84843b73007dae2cb58324",
	"81590911570c8dcb4865a855a0e289206d37323e",
	"c66fb5a1abe7319744d7fc6979180116bcdcd5ac",
	"f522770f2a8b7698f296dee32c66111e96f40bc2",
	"a7200b2d47c799cd9bb0f13f0fdea083985063a1",
	"e1fd92b67f1a61dcb3bdcbbac701ee077dc42862", # import of CartesianCategories
	"c55e5a38a08cad0588ab68b9bf96e9335f6499d9", # import of CartesianCategories

	# Toposes
	"6da9937cf6b4b7dec30bc2af305e65fd216deb06", # outsourcing CartesianCategories
]

def shell_run(command):
	print("(" + command + ")")
	return subprocess.check_output(command, text=True, shell=True)

def shell_run_success(command):
	return subprocess.call(command, shell=True) == 0
	
	
# adapted from gitstats
def getstatsummarycounts(line):
	numbers = re.findall("\d+", line)
	numbers = list(map(int, numbers))
	if len(numbers) == 1:
		# neither insertions nor deletions: may probably only happen for "0 files changed"
		numbers.append(0)
		numbers.append(0)
	elif len(numbers) == 2 and "(+)" in line:
		# only insertions were printed on line
		numbers.append(0)
	elif len(numbers) == 2 and "(-)" in line:
		# only deletions were printed on line
		numbers.insert(1, 0)
	if len(numbers) != 3:
		print("Could not parse shortstat")
		exit(1)
	return numbers

def getdelta(line):
	numbers = getstatsummarycounts(line)
	return numbers[1] - numbers[2]

def get_total_lines_at_commit(commit):
	# diff against empty tree
	output = shell_run("git diff --shortstat `git hash-object -t tree /dev/null` " + commit)
	return getdelta(output)

os.chdir("repos")
repos = os.listdir(".")

diffs = {}
for repo in repos:
	os.chdir(repo)
	
	print("Getting stats for " + repo)
	
	# get a linear history
	lines = shell_run('git log --shortstat --topo-order --reverse --first-parent -m --pretty=format:"%H|%at"').split("\n")

	# get initial commit of the linear history and all additional root commits
	initial_commit_hash = lines[0].split("|")[0]
	root_commit_hashes = shell_run("git rev-list --max-parents=0 HEAD").split("\n")
	if initial_commit_hash not in root_commit_hashes:
		printf("Error: the initial commit is not a root commit")
		exit(1)
	root_commit_hashes.remove(initial_commit_hash)


	if repo == "CAP_project":
		# consider both branches of "The big Sebastian & Sebastian CAP merge" (7da8b677a43c48706bfec06dda584e485f1c68d3), the missing delta of 5081 lines is added explicitly below
		new_lines = shell_run('git log --shortstat --reverse --topo-order --first-parent -m --pretty=format:"%H|%at" ^9d2b34252d1646b4c3d93fccbc97963f554e1d7f e9f9012004c40da3bb10805126033ef9ad6d08c2').split("\n")
		lines.extend(new_lines)
		# CAPCategoryOfProjectiveGradedModules has an unclean subtree merge
		root_commit_hashes.remove("d75e0c53714949becd838f036f599de62ce03c42")
		# CAPManual has an unclean subtree merge
		root_commit_hashes.remove("0d68922f0df4bd3c393196c9e202bb9358f966a5")
		# CartesianCategories has an unclean subtree merge
		root_commit_hashes.remove("84d3c54ae6b7529d7000efe8dcb984c15167f920")

	if repo == "homalg_project":
		root_commit_hashes.append("077a411c5b9482f7726526e97814d8216409e47e")
		root_commit_hashes.append("3f12d921b278ce9494be80bb6811b4ca57f8f067")
		root_commit_hashes.append("edf6b6ece376157cf6c17646c81f49966cc54a53")
		root_commit_hashes.append("d6966aa8647f7c8324fe3b61422d59c767518644")
	
	cumulated_lines = 0

	# for any root commit find merge with the initial commit of the linear history
	# ignore the merge commits and instead consider the log of the subtrees
	blacklist = []
	for root_commit_hash in root_commit_hashes:
		if len(root_commit_hash) == 0:
			continue

		# find first merge commit which is a descendant of initial commit and root commit
		merge_commit_hashes = shell_run("git rev-list --reverse --first-parent --topo-order --merges HEAD").split("\n")
		found_merge_commit_hash = False
		for merge_commit_hash in merge_commit_hashes:
			if shell_run_success("git merge-base --is-ancestor %s %s" % (initial_commit_hash, merge_commit_hash)) and shell_run_success("git merge-base --is-ancestor %s %s" % (root_commit_hash, merge_commit_hash)):
				found_merge_commit_hash = True
				break
		if not found_merge_commit_hash:
			print("Could not find merge commit")
			exit(1)
		
		# consider log of the subtree (second parent of merge commit) instead of merge commit
		blacklist.append(merge_commit_hash)
		parent_commit_hashes = shell_run("git log -n 1 --pretty=%P " + merge_commit_hash).split(" ")
		if len(parent_commit_hashes) != 2:
			print("Merge commit must have exactly two parents")
			exit(1)
		new_lines = shell_run('git log --shortstat --reverse --topo-order --first-parent -m --pretty=format:"%H|%at" ^' + root_commit_hash + ' ' + parent_commit_hashes[1]).split("\n")
		lines.extend(new_lines)

		# consider root commit as an initial commit, i.e. diff against empty tree
		output = shell_run('git log -n 1 --pretty=format:"%at" ' + root_commit_hash)
		timestamp = int(output)
		diff = get_total_lines_at_commit(root_commit_hash)
		if timestamp in diffs:
			print("Error: duplicate timestamp: " + root_commit_hash)
			exit(1)
		diffs[timestamp] = diff
		cumulated_lines += diff
		
	while len(lines) > 0:
		line = lines.pop(0)
		
		if len(line) == 0:
			continue

		parts = line.split("|")
		assert(len(parts) == 2)

		commit_hash = parts[0]
		timestamp = int(parts[1])
		if timestamp in diffs:
			print("Warning: duplicate timestamp: " + commit_hash)
		else:
			diffs[timestamp] = 0
		
		if len(lines) > 0 and "changed" in lines[0]:
			nextline = lines.pop(0)
			diff = getdelta(nextline)
			# fixup CAP commit 7da8b677a43c48706bfec06dda584e485f1c68d3
			if commit_hash == "7da8b677a43c48706bfec06dda584e485f1c68d3":
				diff = 5081
			if commit_hash not in blacklist:
				if abs(diff) >= 10000 and commit_hash not in large_commit_hash_whitelist:
					print("Commit " + commit_hash + " in repo " + repo + " has large diff: " + str(diff))
					exit(1)
				diffs[timestamp] += diff
				cumulated_lines += diff
	
	print("Package " + repo + " has " + str(cumulated_lines) + " lines")
	
	# sanity check: let git compute the total number of lines
	total_lines = get_total_lines_at_commit("HEAD")
	if cumulated_lines != total_lines:
		print("Error: found %d cumulated lines but %d total lines" % (cumulated_lines, total_lines));
		exit(1)
	
	os.chdir("..")

os.chdir("..")

# adapted from gitstats
f = open("lines_of_code.dat", "w")
lines_of_code = 0
for timestamp in sorted(diffs.keys()):
	lines_of_code += diffs[timestamp]
	if timestamp >= start_unix:
		f.write("%d %d\n" % (timestamp, lines_of_code))
f.close()

# png
f = open("lines_of_code_png.plot", "w")
f.write(
"""
set terminal png size 1280,1024
set size 1.0,1.0
set output 'lines_of_code.png'
unset key
set xrange [1167606000:]
set xtics 1167606000,31536000
set yrange [0:]
set xdata time
set timefmt "%s"
set format x "%Y-%m-%d"
set grid x
set grid y
set ylabel "Lines"
set xtics rotate
set bmargin 6
plot 'lines_of_code.dat' using 1:2 w lines
""")
f.close()

shell_run("gnuplot lines_of_code_png.plot")

# svg
f = open("lines_of_code_svg.plot", "w")
f.write(
"""
set terminal svg size 1280,1024
set size 1.0,1.0
set output 'lines_of_code.svg'
unset key
set xrange [1167606000:]
set xtics 1167606000,31536000
set yrange [0:]
set xdata time
set timefmt "%s"
set format x "%Y-%m-%d"
set grid x
set grid y
set ylabel "Lines"
set xtics rotate
set bmargin 6
plot 'lines_of_code.dat' using 1:2 w lines
""")
f.close()

shell_run("gnuplot lines_of_code_svg.plot")
