# When attempting to run_ledaps_landtrendr_processor_#.pro in IDL,
# execution fails if cloudmasks were not generated for one or more
# scenes in the folder. This utility takes scenes which have been
# identified as having no cloudmasks and creates a directory of
# these scenes for targeted runs by the FMASK utility
#
# Author: Trip Hook
# Date: 3/25/2013


import sys, os, subprocess
dates = sys.argv
script = dates.pop(0)
pathrow = dates.pop(0)
root_dir = '/projectnb/trenders/scenes/{0}'.format(pathrow)
search_path = os.path.join(root_dir, "P{0}-R{1}".format(pathrow[0:3], pathrow[3:6]))
output_path = root_dir + "/missing_clouds"
if not os.path.exists(output_path): os.mkdir(output_path)

def duplicateMissedScenes():
    try:
        os.chdir(search_path)
    except:
        sys.exit("Invalid path/row: {0}".format(search_path))

    for a, b, c in os.walk(search_path):
        for date in dates:
            if date in a:
                runstring = "cp -r {0} {1}".format(a, output_path)
                print runstring
                os.system(runstring)

    runstring = 'landsatPrepSubmit.sh -d -c 5 -s 4 -p 12.5 -l 0 -x 0 {0}/missing_clouds'.format(root_dir)
    print runstring
    os.system(runstring)

def addMasksToMaster():
    output_path = '/projectnb/trenders/scenes/040027'
    for a, b, c in os.walk(output_path):
        for f in c:
            if "Fmask" in f and len(a.split("/")) == 6:
                old_path = a + "/" + f
                new_path = a + "/" + a.split("/")[5]
                command = "cp {0} {1}".format(old_path, new_path)
                print command
                os.system(command)


addMasksToMaster()
                
    
    
