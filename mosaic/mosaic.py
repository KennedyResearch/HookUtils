#!/bin/sh
import sys, os, fnmatch

def readDefaults(defaultFile):
    out_dict = {}
    f = open(defaultFile)
    for line in f:
        input_vars = line.split(";")
        if len(input_vars) == 3:
            out_dict[input_vars[1].replace(" ", "")] =\
            r'"{0}"'.format(input_vars[2].replace(" ", "").replace("\n", ""))
    f.close()
    # Specific formatting
    for key in 'searchStrings', 'pathRows', 'bands', 'searchDir', 'rootDir':
        out_dict[key] = out_dict[key].strip("\"").rstrip("\n").split(",")
    return out_dict

def getDirectories(roots, searchDir, pathrows):
    out_list = []
    for pathrow in pathrows:
        for root in roots:
            for d in searchDir:
                new_folder = "{0}/{1}/{2}".format(root, pathrow, d)
                if os.path.exists(new_folder):
                    out_list.append(new_folder)            
    return out_list 
    
def searchDirectory(directory, search_strings):
    local_files = []
    for path, names, files in os.walk(directory):
        for f in files:
            if f.endswith(".bsq"):
                go_ahead = 1
                for search in search_strings:
                    if not fnmatch.fnmatch(f,search): go_ahead = 0
                if go_ahead: local_files.append(path + "/" + f)
    return local_files

def createMosaic(files, bands, outputFile):
    exec_string = "gdalbuildvrt -srcnodata 0 {0}.vrt ".format(outputFile)
    for f in files: exec_string += "{0} ".format(f)
    os.system(exec_string)

    selected_bands = "gdalbuildvrt -separate -srcnodata 0 temp_stack.vrt "
    cleanup = ['temp_stack.vrt']
    for band in bands:
        newfile = "ts_{0}.vrt".format(band)
        os.system("gdal_translate -of VRT -b {0} -a_nodata 0 {1}.vrt {2}".format(band, outputFile, newfile))
        selected_bands += newfile + " "
        cleanup += newfile
    os.system(selected_bands)
    os.system("gdal_translate -of ENVI -a_nodata 0 temp_stack.vrt {0}.bsq".format(outputFile))
    for f in cleanup: os.remove(f)
    print "Created {0}".format(outputFile)
    
def parsePathrow(combos):
    scenes = []
    for combo in combos:
        paths, rows = combo.split("/")
        for l in 'paths', 'rows':
            exec "{0} = {0}.split(\"-\")".format(l)
            exec "{0} = map(int, {0})".format(l)
            exec "if len({0}) == 2 and {0}[0] > {0}[1]: {0} = range({0}[1], {0}[0])".format(l)
            exec "if len({0}) == 2 and {0}[0] < {0}[1]: {0} = range({0}[0], {0}[1])".format(l)
        for path in paths:
            for row in rows:
                scenes.append("{0}{1}".format(str(path).zfill(3), str(row).zfill(3)))
    return scenes

def checkFoundFiles(files, pathrows):
    for pathrow in pathrows:
        found = []
        for f in files:
            if pathrow in f: found.append(f)
        if not found: print "No files found for scene {0}".format(pathrow)
        elif len(found) > 1:
            print "Multiple files found for scene {0}:".format(pathrow)
            for f in found: print "\t {0}".format(f)
        else:
            print "{0}: {1}".format(pathrow, found[0])
                
def main(argv):
    defaultFile = argv[1]
    inputParams = readDefaults(defaultFile)
    for var in inputParams: exec "{0} = {1}".format(var, inputParams[var])
    outputFile = "{0}/{1}".format(outputDir, outMosaic)
    all_files = []
    pathRows = parsePathrow(pathRows)
    for directory in getDirectories(rootDir, searchDir, pathRows):
        for f in searchDirectory(directory, searchStrings):
            all_files.append(f)
    checkFoundFiles(all_files, pathRows)
    createMosaic(all_files, bands, outputFile)
            
if __name__ == '__main__':
    sys.exit(main(sys.argv))
