import os, sys

root_dir = "/projectnb/trenders/scenes"
script = sys.argv[0]
oldPath = sys.argv[1]
oldRow = sys.argv[2]
newPath = sys.argv[3]
newRow =sys.argv[4]

oldShort = "{0}{1}".format(oldPath, oldRow)
newShort = "{0}{1}".format(newPath, newRow)
oldLong = "{0}{1}".format(oldPath.zfill(3), oldRow.zfill(3))
newLong = "{0}{1}".format(newPath.zfill(3), newRow.zfill(3))
oldPR = "P{0}-R{1}".format(oldPath.zfill(3), oldRow.zfill(3))
newPR = "P{0}-R{1}".format(newPath.zfill(3), newRow.zfill(3))

oldDirectory = "{0}/{1}/scripts".format(root_dir, oldLong)
newDirectory = "{0}/{1}/scripts".format(root_dir, newLong)

if not os.path.exists(oldDirectory): sys.exit("No templates found in {0}".format(oldDirectory))
if os.path.exists(newDirectory): os.system("rm -r {0}".format(newDirectory))
os.mkdir(newDirectory)

os.system("cp {0}/* {1}".format(oldDirectory, newDirectory))
os.system("rm {0}/*.e*".format(newDirectory))
os.system("rm {0}/*.o*".format(newDirectory))

for a, b, c in os.walk(newDirectory):
    for f in c:
        full = a + "/" + f
        oldlines = []
        g = open(full, 'rb')
        for line in g: oldlines.append(line)
        g.close()
        newfile = f
        for nameType in 'Short', 'Long', 'PR':
            newlines = []
            exec 'oldName = old{0}'.format(nameType)
            exec 'newName = new{0}'.format(nameType)
            newfile = newfile.replace(oldName, newName)
            for line in oldlines: newlines.append(line.replace(oldName, newName))
            oldlines = newlines
        newfile = "{0}/{1}".format(a, newfile)
        g = open(newfile, 'w')
        for line in newlines: g.write(line)
        g.close()
        os.remove(full)


            



