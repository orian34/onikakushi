# PS3 Voice and Graphics Patch
#### For Higurashi No Naku Koro Ni - Chapter 1 Onikakushi

> This repository **only** hosts the script files and a few voice files needed to fix bugs, check our [wiki](https://github.com/07th-mod/guide/wiki/Higurashi-Getting-started) for instructions on how to install the patch!

This patch aims to combine the efforts of the ps3 voice patch and the ps3 sprites/background patch, and fill in missing voice files not covered by the original voice patch.

# Installing the patch

> [Check our wiki](https://07th-mod.com/wiki/).

# Releases

https://github.com/07th-mod/onikakushi/releases/

This repository is in constant change. Sometimes new releases might get on hold until there is enough content to push a new patch. If the latest patch has a bug that seems to be already fixed in the repository, try downloading the master file. The master file will always have the latest files, regardless of the current release being outdated or not.

# Developing with us

Usually, older contributors are welcome to join the repository and push their own changes without supervision. However, you can also aid the development just by forking the repository and working on your own changes. After you are done, commit the changes, make a pull request and if it's good enough, the changes will be merged. Both approaches are more than welcome!

## Publishing new releases

Github Actions is setup to automatically build and publish every tagged commit. When you want to create a new release:

- tag the latest commit (`git tag v1.2.3`)
- push the tag to github (`git push --tags`)
- wait for the build to finish
- on github, check the 'Releases' tab for a new draft release
- edit this draft as needed, then publish this draft

(your git GUI can probably do this without entering any commands)

## Updating the installer

The `installData.json` file of the installer must be updated each time a new release is published to update the download links.

To update the links

- navigate inside the `update_installdata_urls` folder
- run `update_installdata_urls.bat`. This will produce an updated `installData.json`
- overwrite the `installData.json` in the [07th-mod/python-patcher repo](https://github.com/07th-mod/python-patcher)
- double check the changes seem correct (should just update URLs in the .json file)
- push the updated `installData.json` file to the python-patcher repo

# Credits

- @enumag - For coding the new automation script
- @Grelo - For updating the graphics patch entirely
- Anon - For giving us the PS3 files and scripts
- TheGuraGuraMan - For making the Sprite/BGM Patch
- Another Anon - For providing the watermark-less window
- @Norgus - For helping us reach v2 with thousands of fixes
- @IrlPM - For helping with the 1440p Sprites and a lot of new features
- @idealpersona and drojf  - For Making the Movie Support
- @Inochi-PM - For making the whole new UI.
