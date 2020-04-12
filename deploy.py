import glob
import hashlib
import os
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import Callable, Any

# !! Please set this variable to the correct Data Folder Name !!
HIGURASHIEP0X_FOLDER = 'HigurashiEp01_Data'
# !! Please set this variable to the correct Data Folder Name !!


# Paths and Filenames
STAGING_FOLDER = '07th-mod-french-patch-staging'
HIGURASHIEP0X_DATA_PATH = os.path.join(STAGING_FOLDER, HIGURASHIEP0X_FOLDER)
STREAMING_ASSETS_PATH = os.path.join(HIGURASHIEP0X_DATA_PATH, 'StreamingAssets')
OUTPUT_ARCHIVE_NAME = 'built_release.7z'

IS_WINDOWS = sys.platform == "win32"

# The github ref - note that it is something like "refs/tags/v1.9.4"
GITHUB_REF = os.environ.get('GITHUB_REF')


def group_by(values: list, keyFunc: Callable[[Any], Any]) -> dict:
	"""
	This function groups 'values' according to the keyFunc.
	All values where keyFunc(value) is the same (called the 'key') will be grouped together.

	This function differs from itertools.groupby() in that it doesn't require the input be sorted.
	It will also preserve the order of the input values
	:return: A dict of the form keyFunc(value): List[Any], with one entry for each key paired with its grouped values
	"""
	# Don't use defaultdict as user will expect a regular dict returned
	grouped = {}

	for value in values:
		key = keyFunc(value)
		if key not in grouped:
			grouped[key] = []

		grouped[key].append(value)

	return grouped


def try_remove_tree(path):
	try:
		if os.path.isdir(path):
			shutil.rmtree(path)
		else:
			os.remove(path)
	except FileNotFoundError:
		pass


def try_remove_tree_repeat_attempt(folder_to_remove, num_attempts=5):
	last_exception = None
	for attempt in range(num_attempts):
		print(f'Attempt {attempt} to remove {folder_to_remove}')
		try:
			try_remove_tree(folder_to_remove)
			return
		except Exception as e:
			last_exception = e
			traceback.print_exc()
			time.sleep(1)

	raise last_exception


def call(args, **kwargs):
	print("running: {}".format(args))
	retcode = subprocess.call(args, shell=IS_WINDOWS, **kwargs) # use shell on windows
	if retcode != 0:
		exit(retcode)


# Long options: 7z a -m0=lzma2 -mmt=3 -mx=9 -mfb=64 -md=256m -ms=on out.7z HigurashiEp04_Data
# Short options: 7z a -m0=lzma2 -mx=9 -md=256m -mmt=3 out.7z HigurashiEp04_Data
def archive(input_path, output_filename):
	try_remove_tree(output_filename)
	call(["7z", "a",
		  "-mx=9",     # max compression level
		  "-md=256m",  # 256m dictionary size (memory used for compression is much higher than this)
		  "-mmt=3",    # use 3 threads (using > 3 threads results in increased archive size)
		  output_filename, input_path])


def hash_file(file_path: str):
	BLOCKSIZE = 65536
	file_hash = hashlib.blake2b()

	with open(file_path, "rb") as f:
		chunk = f.read(BLOCKSIZE)
		while len(chunk) > 0:
			file_hash.update(chunk)
			chunk = f.read(BLOCKSIZE)

	return file_hash.digest(), file_hash.hexdigest()


def get_unity_version_from_file(filepath):
	with open(filepath, 'rb') as file:
		_ = file.read(20)
		version_string = file.read(7)
		return version_string.decode('utf-8')


def extract_details_from_sharedasset(path: str):
	unity_version = get_unity_version_from_file(path)

	part_path, _ = os.path.split(path)
	part_path, store = os.path.split(part_path)
	part_path, operating_system = os.path.split(part_path)

	return operating_system, store, unity_version


def get_assets_grouped_by_hash(ui_folder: str):
	hash_to_paths = {}

	# Hash every sharedasset
	for path_object in Path(ui_folder).rglob('*.assets'):
		path = str(path_object)
		hash, hexdigest = hash_file(path)
		print(f"Hashed {path:50} as {hexdigest[:20]}...{hexdigest[-20:]}")

		if hash not in hash_to_paths:
			hash_to_paths[hash] = []

		hash_to_paths[hash].append(path)

	return hash_to_paths.values()


def get_asset_grouped_by_os_and_unity_version(ui_folder: str):
	# Iterate through all the assets and fetch their os, store, and unity version
	all_assets = []
	for path_object in Path(ui_folder).rglob('*.assets'):
		path = str(path_object)
		operating_system, store, unity_version = extract_details_from_sharedasset(path)
		all_assets.append((path, operating_system, store, unity_version))

	# Group assets by os (either Windows or MacOS_Linux)
	grouped_by_os = list(group_by(all_assets, lambda x: x[1]).values())

	# Further group assets by same unity version
	groups = []
	for group in grouped_by_os:
		subgroup = list(group_by(group, lambda x: x[3]).values())
		groups.extend(subgroup)

	# Copy out just the paths
	return [[asset[0] for asset in asset_group] for asset_group in groups]


def deploy_shared_assets(group_by_hash=False):
	if group_by_hash:
		grouped_paths = get_assets_grouped_by_hash('UI')
	else:
		grouped_paths = get_asset_grouped_by_os_and_unity_version('UI')

	for path_group in grouped_paths:
		all_os = set()
		all_stores = set()
		all_unity_version = set()

		for path in path_group:
			operating_system, store, unity_version = extract_details_from_sharedasset(str(path))
			# Rename details 07th-mod installer's convention
			if operating_system.lower() == 'macos_linux':
				operating_system = 'LinuxMac'
			if store.lower() == 'mangagamer':
				store = 'MG'
			all_os.add(operating_system)
			all_stores.add(store)
			all_unity_version.add(unity_version)

		if len(all_unity_version) != 1:
			raise Exception("Files were identical but had different unity versions or no unity versions")

		all_os = sorted(list(all_os))
		all_stores = sorted(list(all_stores))
		unity_version = all_unity_version.pop()

		output_filename = f"{'-'.join(all_os)}-{'-'.join(all_stores)}-{unity_version}.assets"
		is_default_ui = 'windows' in output_filename.lower() and 'steam' in output_filename.lower()
		if is_default_ui:
			output_filename = 'sharedassets0.assets'

		output_path = os.path.join(HIGURASHIEP0X_DATA_PATH, output_filename)
		containing_dir, _ = os.path.split(output_path)
		os.makedirs(containing_dir, exist_ok=True)

		print(f'Copying {path_group[0]} as {output_filename}{("" if not is_default_ui else " [Default/Steam]")}')
		shutil.copy(path_group[0], output_path)


def deploy():
	print("------------------------------------------------------------------------------------")
	print(f"Deploying release {GITHUB_REF}")

	try_remove_tree_repeat_attempt(STAGING_FOLDER)

	deploy_shared_assets()

	os.makedirs(STAGING_FOLDER, exist_ok=True)

	# Copy CG and Update folders to StreamingAssets folder
	shutil.copytree('CG', os.path.join(STREAMING_ASSETS_PATH, 'CG'))
	shutil.copytree('Update', os.path.join(STREAMING_ASSETS_PATH, 'Update'))

	# Copy .json files inside the HigurashiE0x_Data folder
	for jsonFile in glob.glob(f'*.json'):
		shutil.copy(jsonFile, os.path.join(HIGURASHIEP0X_DATA_PATH, jsonFile))

	# Archive the HigurashiE0x_Data folder
	archive(f'./{HIGURASHIEP0X_DATA_PATH}', os.path.join(STAGING_FOLDER, OUTPUT_ARCHIVE_NAME))

	print(f"Finished deploying {GITHUB_REF}!")
	print("------------------------------------------------------------------------------------")


if __name__ == '__main__':
	deploy()
