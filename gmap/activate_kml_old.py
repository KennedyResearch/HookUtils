## TO DO
## Sort into folders for C-Monster et al

import csv, os
import os.path
import gdata.data
import gdata.acl.data
import gdata.docs.client
import gdata.docs.data
import gdata.sample_util
from apiclient import errors
from dropbox import client, rest, session
import gdata.docs
import gdata.docs.service
import gdata.spreadsheet.service
import re, os

username        = 'landtrendr@gmail.com'
passwd          = 'landtrendr4U'
doc_name        = 'LT_Status'
header_row      =  2



os.chdir('/projectnb/trenders/hook_utils/gmap')
local_file = "active.kml"
remote_file = "ltr_prog.kml"
remote_key = 'LT_Status'

# Processing mode
create_new_kml = 1
imbue_with_data = 1

# Only needed when creating new kml
hexagons = "/projectnb/trenders/scenes/scene_bounds/EPSG4326/wrs_projected.shp"
id_field = "PATHROW"

# Only needed when updating existing kml
key_file = "key.csv"
color_key = "color_adjust.csv"
path_h, row_h, stage_h = "path", "row", "color"

def createGoogleClient():
  # Connect to Google
  cl = gdata.spreadsheet.service.SpreadsheetsService()
  cl.email = username
  cl.password = passwd
  cl.source = 'payne.org-example-1'
  cl.ProgrammaticLogin()
  return cl

def uploadKML(localFile, remoteFile):
  def google():
      class SampleConfig(object):
        APP_NAME = 'GDataDocumentsListAPISample-v1.0'
        DEBUG = False
      """Create a Documents List Client."""
      client = gdata.docs.client.DocsClient(source=SampleConfig.APP_NAME)
      client.http_client.debug = SampleConfig.DEBUG
      client.ClientLogin("landtrendr@gmail.com", "landtrendr4U", client.source)
      return client
    """Upload a document, unconverted."""
    client = CreateClient()
    doc = gdata.docs.data.Resource(type='kml', title=remoteFile)
    media = gdata.data.MediaSource()
    media.SetFileHandle(localFile, 'application/msword')
    # Pass the convert=false parameter
    create_uri = gdata.docs.client.RESOURCE_UPLOAD_URI + '?convert=false'
    doc = client.CreateResource(doc, create_uri=create_uri, media=media)
    doc = client.UpdateResource(doc, media=media, new_revision=True)
    print 'Created, and uploaded:', doc.title.text, doc.resource_id.text

  def dropbox():
    # Get your app key and secret from the Dropbox developer website
    APP_KEY, APP_SECRET = 'rcxvutuv01jqf25', 'efne6uegb1mebsj'
    OAUTH_KEY, OAUTH_SECRET = 'tj94yakmcjjzeq5', 'z28fxcb1hw1bwwr'
    sess = session.DropboxSession(APP_KEY, APP_SECRET, 'app_folder')
    sess.set_token(OAUTH_KEY, OAUTH_SECRET)
    cl = client.DropboxClient(sess)
    f = open(localFile)
    response1 = cl.file_delete(remote_file)
    response = cl.put_file(remote_file, f)
    f.close()

  # Method to use
  dropbox()
  
def updateKML():   
    def strip(string, tags):
        for tag in tags: string = string.replace(tag, "")
        return string

    def xmlFormat(string):
        for char in ["&", "<", ">", "\"", "-", "\n", "\r"]:
          string = string.replace(char, "*")
        return string

    def setColorScheme(kml, color_map):
        def readColorMap(cmap):
            outdict = {}
            f = open(color_map, "rb")
            reader = csv.DictReader(f)
            for line in reader: outdict[line['CODE']] = line
            f.close()
            return outdict

        def addString(cmap):
            outstring = ""
            for code in cmap:
                outstring += "\
\t\t<Style id=\"Stage{0}\">\n\
\t\t\t<LabelStyle>\n\
\t\t\t\t<color>{1}</color>\n\
\t\t\t</LabelStyle>\n\
\t\t\t<LineStyle>\n\
\t\t\t\t<color>{2}</color>\n\
\t\t\t\t<width>0.400000</width>\n\
\t\t\t</LineStyle>\n\
\t\t\t<PolyStyle>\n\
\t\t\t\t<color>{3}</color>\n\
\t\t\t\t<outline>1</outline>\n\
\t\t\t</PolyStyle>\n\
\t\t</Style>\n".format(code, cmap[code]["LABEL"],cmap[code]["LINE"],cmap[code]["POLY"])
            return outstring

        def addHeader(k, header):
            cleanOld(k, "Style")
            f = open(k, 'rb')
            g = ""
            for line in f:
                g += line
                if "<Document>" in line: g += header
            f.close()
            modifyFile(k,g)               

        gd_client = createGoogleClient()
        c_map = readColorMap(color_map)
        styleHeader = addString(c_map)
        addHeader(kml, styleHeader)
        
    def readKey(keyfile, header_row = 1):
        out_dict = {}
        # Read column headings
        f = open(keyfile, 'rb')
        for i in range(header_row): header = f.readline().split(",")
        f.close()
        for h in path_h, row_h, stage_h:
            if not h in header: sys.exit("Header {0} not identified in key file. Adjust row number or heading names".format(h))

        # Read file into dictionary
        f = open(keyfile, 'rb')
        reader = csv.DictReader(f, header)
        for line in reader:
            path, row, stage = str(line[path_h]), str(line[row_h].zfill(3)), line[stage_h]
            try:
                a, b, c = int(path), int(row), int(stage)
                new_dict = {}
                for key in line: new_dict[strip(key, ["\n", "\r", "\t", "\""])] = line[key]
                out_dict[path+row] = new_dict
                out_dict[path+row]["Map"] = stage
                out_dict[path+row]["Name"] = "Path {0} Row {1}".format(path, row.zfill(2))
            except: pass
        return out_dict
  
    def readKeyNew(kml):

      q = gdata.spreadsheet.service.DocumentQuery()
      q['title'] = kml
      q['title-exact'] = 'true'
      feed = gd_client.GetSpreadsheetsFeed(query=q)
      spreadsheet_id = feed.entry[0].id.text.rsplit('/',1)[1]
      feed = gd_client.GetWorksheetsFeed(spreadsheet_id)
      worksheet_id = feed.entry[0].id.text.rsplit('/',1)[1]

      out_dict = {}
      rows = gd_client.GetListFeed(spreadsheet_id, worksheet_id).entry
      for row in rows:
          line = {}
          custom = row.custom
          for key in custom:
              line[key] = custom[key].text
              try:
                    path, row, stage = str(line[path_h]), str(line[row_h].zfill(3)), line[stage_h]
                    a, b, c = int(path), int(row), int(stage)
                    new_dict = {}
                    for key in line: new_dict[strip(key, ["\n", "\r", "\t", "\""])] = line[key]
                    out_dict[path+row] = new_dict
                    out_dict[path+row]["Map"] = stage
                    out_dict[path+row]["Name"] = "Path {0} Row {1}".format(path, row.zfill(2))
              except: pass
      return out_dict

    def createTags(tag_dict, tag_id):
        outstring = "\
\t\t\t\t<name>{0}</name>\n\
\t\t\t\t<styleUrl>#Stage{1}</styleUrl>\n\
\t\t\t\t<description>\n\
\t\t\t\t\t<![CDATA[\n\
\t\t\t\t\t\t<div style=\"height:150px;overflow:scroll\">\n\
\t\t\t\t\t\t\t<table border=1>\n".format(tag_dict['Name'], tag_dict['Map'])
        for tag in tag_dict:
            outstring += "\
\t\t\t\t\t\t\t\t<tr><td>{0}</td><td>{1}</td></tr>\n".format(
      tag, xmlFormat(str(tag_dict[tag])))
        outstring += "\
\t\t\t\t\t\t\t</table>\n\
\t\t\t\t\t\t</div>\n\
\t\t\t\t\t]]>\n\
\t\t\t\t</description>\n"
        return outstring   

    def modifyFile(filePath, newContents):
        tmp = filePath + "tmp"
        f = open(tmp, "w")
        f.write(newContents)
        f.close()
        os.remove(filePath)
        os.rename(tmp, filePath)

    def cleanOld(k, bracket):
        f = open(k, "rb")
        g = ""
        for line in f:
            if "<name>" in line: line = f.next()
            if "<{0}".format(bracket) in line:
                searchline = line
                while not "</{0}".format(bracket) in searchline: searchline = f.next()
                line = f.next()
            g += line
        f.close()
        modifyFile(k, g)
        
    def modifyTags(kml, key_dict):
        cleanOld(kml, "Extended")
        f = open(kml, "rb")
        g = ""
        for line in f:
            if "<Placemark" in line:
                pid = strip(line, ["<Placemark id=\"", "\">", "\r","\n", " "])
                if pid in key_dict.keys(): g += "{0}\n{1}".format(line, key_dict[pid]['tags'])
                else:
                  searchline = line
                  while not "</Placemark" in searchline: searchline = f.next()
            elif strip(line, [" ", "\n", "r"]): g += line
        f.close()
        modifyFile(kml, g.expandtabs(1))

    setColorScheme(local_file, color_key) 
    key = readKeyNew(remote_key)
    for polygon in key: key[polygon]['tags'] = createTags(key[polygon], polygon)
    modifyTags(local_file, key)


def createKML():
    import ogr

    header = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n\
\t<Document>\n\
\t\t<Folder>\n\
\t\t<name>Landsat Scenes</name>\n\
\t\t<visibility>1</visibility>\n\
\t\t<description>Landsat scenes and the progress of their LandTrendr analysis</description>"

    footer = "\t\t</Folder>\n\t</Document>\n</kml>"


    def generateCoordinates(shapefile, idf):
        def readShapes(shapefile):
            outdict = {}
            ds = ogr.Open(shapefile)
            layer1 = ds.GetLayer(0)   
            for feat in layer1:
                poly_id = feat.GetFieldAsString(idf)
                geom = feat.GetGeometryRef()
                ring = geom.GetGeometryRef(0)
                points = ring.GetPointCount()
                vertices = []
                for p in xrange(points):
                    lon, lat, z = ring.GetPoint(p)
                    vertices.append((lon, lat))
                outdict[poly_id] = vertices
            return outdict
                    
                
        point_header, point_footer = "\
\t\t\t\t<Polygon>\n\
\t\t\t\t\t<extrude>0</extrude>\n\
\t\t\t\t\t<altitudeMode>clampedToGround</altitudeMode>\n\
\t\t\t\t\t<outerBoundaryIs>\n\
\t\t\t\t\t\t<LinearRing>\n\
\t\t\t\t\t\t\t<coordinates>\n", "\
\t\t\t\t\t\t\t</coordinates>\n\
\t\t\t\t\t\t</LinearRing>\n\
\t\t\t\t\t</outerBoundaryIs>\n\
\t\t\t\t</Polygon>\n"

        outdict = {}
        shapes = readShapes(shapefile)
        for shape in shapes:
            vertices = shapes[shape]
            outdict[shape] = point_header
            for vertex in vertices: outdict[shape] += "\t\t\t\t\t\t\t\t{0},{1}\n".format(vertex[0], vertex[1])
            outdict[shape] += point_footer
        return outdict

    def writeFile(outfile, outputString):
        f = open(outfile, 'w')
        f.write(outputString)
        f.close()

    outstring = header    
    coords = generateCoordinates(hexagons, id_field)
    for name in coords:
        outstring += "\n\t\t\t<Placemark id=\"{0}\">\n{1}\t\t\t</Placemark>\n".format(name, coords[name])
    outstring += footer
    writeFile(local_file, outstring.expandtabs(1))

if create_new_kml: createKML()
if imbue_with_data: updateKML()

uploadKML(local_file, remote_file)
