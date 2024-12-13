# Downloading multiple .rod files

## download_rods_script.sh

Adjust the file `download_rods_script.sh`to the range of download you want.
Default start is `1` and default end is `3`.
Be careful: Do not trigger unneccsary amounts of downloads.

Take a look [here](https://solsa.crystallography.net/rod/1000679.html), to get valid .rod IDs. For this example its e.g. `1000679`.

## Add the command as script

`chmod +x download_rods_script.sh`

## Exectutute the script

`./download_rods_script.sh`


## Convert the downloaded .rod files

via the pynxtools-raman command:

`dataconverter <PATH_TO>/1000679.rod src/pynxtools_raman/config/config_file_rod.json --reader raman --nxdl NXraman --output rod_example_neuxs.nxs`


# Automatec conversion of all .rod files to .nxs files

## Add the command as script
`chmod +x convert_all_rod_to_nxs.sh`

## Call the script
`./src/download_rod_files/convert_all_rod_to_nxs.sh`

