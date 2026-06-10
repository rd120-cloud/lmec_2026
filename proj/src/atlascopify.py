#!/usr/bin/env python3

import argparse
import requests
import os
import json
import copy
import subprocess
from osgeo import gdal
import shapely as geom
from shapely.geometry import Polygon, MultiPolygon
from pyproj import Geod
import pandas as pd
import numpy as np
import geopandas as gpd
from pyproj import Transformer
from os import path
from functools import partial
import traceback
import glob
import csv

#########################################
#####                               #####
#####    STEP 0: set arguments      #####
#####    so script can be run       #####
#####    from the command line      #####
#####                               #####
#########################################

parser = argparse.ArgumentParser(description='Tools to help in the process of geotransforming urban atlases.')
parser.add_argument('--step', metavar='{download-inputs, allmaps-transform, warp-plates, mosaic-plates, create-xyz, write-extents, write-wasabi}', type=str, 
                    help='steps to execute (default: download-inputs)', default='download-inputs', dest='step')
parser.add_argument('-id', '--identifier', type=str, 
                    help='commonwealth id', dest='identifier')
args = parser.parse_args()

def proceed(nextFunction, *args, **kwargs):
    choice = input(f"Do you want to proceed to {nextFunction.__name__}? (y/n): ").strip().lower()
    if choice == "y":
        nextFunction(*args, **kwargs)

#########################################
#####                               #####
#####    STEP 1: `downloadInputs`   #####
#####    to retrieve all georef     #####
#####    annotations and images     #####
#####                               #####
#########################################

def downloadInputs(identifier):

    # get Allmaps manifest as JSON
    # create empty list to hold image filenames

    allmapsManifest = requests.get(f'https://annotations.allmaps.org/?url=https://www.digitalcommonwealth.org/search/{identifier}/manifest.json').json()

    # download each map in the manifest
    # and save as .json file

    print(f"\nBeginning to download {len((allmapsManifest)['items'])} annotations...\n")
    for item in allmapsManifest['items']:
        allmapsMapURL = item['id']
        print(f'⤵️ Downloading annotation {allmapsMapURL}')
        allmapsAnnotation = requests.get(allmapsMapURL, stream=True).json()
        with open(f'./tmp/annotations/{allmapsMapURL[-16:]}.json', 'w') as f:
            json.dump(allmapsAnnotation, f)
    
    print("✅   All annotations downloaded!")

    # download any images not present in directory

    for item in allmapsManifest["items"]:
        imgManifest = item["target"]["source"]["id"]
        imgID = imgManifest.split("commonwealth:")[1][0:9]
        imgURL=f"https://curator.digitalcommonwealth.org/api/filestreams/image/commonwealth:{imgID}?show_primary_url=true"
        imgFile = f'./tmp/img/{imgID}.tif'
        if os.path.isfile(imgFile) == True:
            print(f'⏭️ Skipping {imgFile}, already exists...')
        else:
            print(f'⤵️ Downloading image {imgManifest}')
            imageRequest = requests.get(imgURL, stream=True)
            response = imageRequest.json()
            img = requests.get(response['file_set']['image_primary_url'])
            with open(imgFile, 'wb') as fd:
                for chunk in img.iter_content(chunk_size=128):
                    fd.write(chunk)

    print("✅   All images downloaded!")
    
    # create tileset.json template

    print("Creating template `tileset.json` file...")

    template = requests.get("https://raw.githubusercontent.com/bplmaps/atlascope-utilities/master/modern-workflow/template.json").json()
    tileset = open('output/tileset.json', 'w+')
    tileset.write(json.dumps(template, indent=2))
    tileset.close()

    print("✅   Template `tileset.json` file created in `output` directory!\n")

    proceed(allmapsTransform, identifier)

#########################################
#####                               #####
#####   STEP 2: `allmapsTransform`  #####
#####   to transform pixel mask     #####
#####       into a .geojson         #####
#####                               #####
#########################################

def allmapsTransform(identifier):
    
    # define path variables and lists for error handling

    path = "./tmp/annotations/"
    outPath = path+"transformed/"

    # loop through `path` and 
    # transform each JSON into GeoJSON
    # using Allmaps CLI as subprocess
    
    for f in os.listdir(path):
        mapId = os.path.splitext(f)[0]
        isFile = os.path.isfile(path+f)
        
        if not f.startswith('.') and isFile == True:
            
            d=json.load(open(path+f))
            if ((d['body']['features'])):
                
                print(f'⤵️ Transforming {f} into a geojson...')
                name = os.path.splitext(f)[0]+'-transformed.geojson'
                footprint = open(outPath+name, "w")
                cmd = ["allmaps", "transform", "resource-mask", f]
                subprocess.run(cmd, cwd=path, stdout=footprint)
                plateSchema = {"geometry": "Polygon", "properties": {"imageId": "str"}}
                
                try:
                    gdf = gpd.read_file(outPath+name)
                    request = requests.get(f'https://api.allmaps.org/maps/{mapId}')
                    response = request.json()
                    uri = response['_allmaps']['id'][-16:]
                    gdf.to_file(outPath+name, driver="GeoJSON", schema=plateSchema)
                except:
                    print("Someting went wrong!")

            # save geojson to file
        
    # merge, dissolve, specify precision

    print("✅   All pixel masks transformed!\n")
    print("Generating `plates.geojson` file...\n")


    # merge masks using geopandas

    masks = glob.iglob(outPath+'*.geojson')
    plates = gpd.pd.concat([gpd.read_file(mask) for mask in masks])
    fields = ['identifier', 'name', 'allmapsMapID', 'digitalCollectionsPermalinkPlate']
    plates[fields] = ''
    polySchema = {"geometry": "Polygon", "properties": {"imageId": "str", "identifier": "str", "name": "str", "allmapsMapID": "str", "digitalCollectionsPermalinkPlate": "str"}}
    multipolySchema = {"geometry": "MultiPolygon", "properties": {"imageId": "str", "identifier": "str", "name": "str", "allmapsMapID": "str", "digitalCollectionsPermalinkPlate": "str"}}
    plates.to_file("output/plates.geojson", driver="GeoJSON", schema=polySchema)

    # dissolve plates file and
    # save according to geometry type
    
    try:
        diss = plates.dissolve()
        multiPolyCheck = 'MultiPolygon' in diss['geometry'].geom_type.values
        if multiPolyCheck == True:
            diss.to_file("tmp/plates-dissolved.geojson", driver="GeoJSON", schema=multipolySchema)
        else:
            diss.to_file("tmp/plates-dissolved.geojson", driver="GeoJSON", schema=polySchema)
        if os.path.exists("tmp/errors") == True:
            print("You can delete the `tmp/errors` directory.\n")
        print("✅   All `plates` files have been created!\n")
        print("You can now proceed to the `warp-plates` step.\n")
    except RuntimeError as e:
        print(e)
    
    # trim to 4 decimal pts

    out=open("plates-precise.geojson", "w")
    cmd=["mapshaper", "plates-dissolved.geojson", "-o", "precision=0.0001", "plates-precise.geojson"]
    subprocess.run(cmd, cwd="tmp/", stdout=out)

    # populate tileset with appropriate metadata

    with open('tmp/plates-precise.geojson') as f:
        d = json.load(f)
        coords=d['features'][0]['geometry']['coordinates']

    geom=MultiPolygon([Polygon(ring[0]) for ring in coords]) if len(coords) > 1 else Polygon(coords[0])


    gdf = gpd.GeoDataFrame(
        geometry=[geom],
        crs="EPSG:4326"
    )

    template = requests.get("https://raw.githubusercontent.com/bplmaps/atlascope-utilities/master/modern-workflow/template.json")
    data = template.json()
    ark_id = os.path.basename(os.getcwd())

    if identifier:
        manifest=f"https://www.digitalcommonwealth.org/search/{identifier}/manifest.json"
        metadata = requests.get(manifest).json()
        data['description'] = f"{metadata['label']} ({metadata['metadata'][2]['value']}, {metadata['metadata'][1]['value']})"

    data['bounds'] = gdf.total_bounds.tolist()
    data['tiles'] = [f"https://s3.us-east-2.wasabisys.com/urbanatlases/{ark_id}/tiles/{{z}}/{{x}}/{{y}}.png"]
    data['data'] = [f"https://s3.us-east-2.wasabisys.com/urbanatlases/{ark_id}/plates.geojson"]

    with open("output/tileset.json", "w") as f:
        json.dump(data, f, indent=4)
    
    proceed(warpPlates)

#########################################
#####                               #####
#####       STEP 3: `warpPlates`    #####
#####       to turn map images      #####
#####         into GeoTIFFs         #####
#####                               #####
#########################################

def warpPlates():

    # set transformation and path variables

    gdal.UseExceptions()
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    path="./tmp/annotations/"

    # loop through annotations and
    # perform GDAL warp

    for file in os.listdir(path):
        isFile = os.path.isfile(path+file)
        if not file.startswith('.') and isFile == True:

            print(f'🏔   Registering GCPs from annotation...')
            annotation = json.load(open(path+file))
            commonwealthUrl = annotation['target']['source']['partOf'][0]['id']
            commId = (commonwealthUrl[-9:])
            
            # correlate pixel and spatial coordinates
            
            gcps = []
            for gcp in annotation['body']['features']:
                    # print(gcp['properties']['resourceCoords'])
                    xt, yt = transformer.transform(
                        gcp['geometry']['coordinates'][0], gcp['geometry']['coordinates'][1])
                    line = float(gcp['properties']['resourceCoords'][1])
                    pixel = float(gcp['properties']['resourceCoords'][0])
                    g = gdal.GCP(xt, yt, 0, pixel, line)
                    gcps.append(g)
            sourceImg = gdal.Open(f'./tmp/img/{commId}.tif')
            
            # # nearblack hack

            # for b in [1, 2, 3]:
            # 	band = archivalImage.GetRasterBand(b)
            # 	readableBand = band.ReadAsArray()
            # 	readableBand[np.where(readableBand == 0)] = 1

            # set variables for GDAL translate and
            # execute

            translateOptions = gdal.TranslateOptions(
                format='GTiff',
                GCPs=gcps,
                outputSRS='EPSG:3857'
            )
            
            mapId = os.path.splitext(file)[0]

            gdal.Translate(
                f'./tmp/img/{mapId}-translated.tif',
                sourceImg,
                options = translateOptions
            )
                        
            # set options for GDAL warp and
            # execute

            cutline = f'./tmp/annotations/transformed/{mapId}-transformed.geojson'
            
            # calc area to dynamically set x/yres
            with open(cutline) as f:
                features = json.load(f)["features"]
            polygon = Polygon(features[0]["geometry"]["coordinates"][0])
            geod = Geod(ellps="WGS84")
            poly_area = geod.geometry_area_perimeter(polygon)[0]

            warpOptions = gdal.WarpOptions(
                                    format='GTiff',
                                    copyMetadata=True,
                                    multithread=True,
                                    dstSRS="EPSG:3857",
                                    creationOptions=['COMPRESS=LZW', 'BIGTIFF=YES'],
                                    polynomialOrder=1,
                                    resampleAlg='cubic',
                                    dstAlpha=True,
                                    dstNodata=0,
                                    xRes=0.1 if poly_area < 50000000 else 0.3,
                                    yRes=0.1 if poly_area < 50000000 else 0.3,
                                    targetAlignedPixels=True,
                                    cutlineDSName=cutline,
                                    cropToCutline=True,
                                    )
            warpedPlate = f'./tmp/warped/{mapId}-warped.tif'
            isFile = os.path.isfile(warpedPlate)

            if isFile == True:
                print(f'⏭️   Skipping {warpedPlate}, already exists...')
                os.remove(f'./tmp/img/{mapId}-translated.tif')
            else:
                print(f'💫 Creating warped TIFF in EPSG:3857 for {mapId}.json')
                gdal.Warp(f'./tmp/warped/{mapId}-warped.tif',
                            f'./tmp/img/{mapId}-translated.tif', options=warpOptions)

                print(f'🚮   Deleting temporary translate file for {mapId}.json')
                os.remove(f'./tmp/img/{mapId}-translated.tif')
    
    proceed(mosaicPlates)

#########################################
#####                               #####
#####     STEP 4: `mosaicPlates`    #####
#####      to create virtually      #####
#####        mosaiqued raster       #####
#####                               #####
#########################################

def mosaicPlates():

    # define vrt options and orderFile exist variable

    vrtOptions = gdal.BuildVRTOptions(
        resolution = 'highest',
        outputSRS = 'EPSG:3857',
        separate = False,
        srcNodata = 0
        )
    orderFile = os.path.exists("tmp/sort-order.txt")

    if orderFile == True:
        platesForMosaic = open("tmp/sort-order.txt", "r")
        path = "tmp/warped/"
        print('➡️  Beginning to create VRT')
        gdal.BuildVRT('tmp/mosaic.vrt', platesForMosaic, options=vrtOptions)
        print('🎉 Created the VRT. You can now run the final command, `create-xyz`!')

    else:
        platesForMosaic = []
        warpedPlates = {}
        path = "tmp/warped/"

        # sort plates from small to large

        for f in os.listdir(path):
            isFile = os.path.isfile(path+f)
            if not f.startswith('.') and isFile == True and f.endswith('.tif'):
                plate = path+f
                size = os.path.getsize(plate)
                warpedPlates[plate] = size
        sortedPlates = sorted(warpedPlates.items(), key=lambda x:x[1], reverse=True)

        # append sorted files to new list to be mosaiqued

        for f in sortedPlates:
            platesForMosaic.append(f[0])

        print('➡️  Beginning to create VRT')

        gdal.BuildVRT('tmp/mosaic.vrt', platesForMosaic, options=vrtOptions)

        print('🎉 Completed creating the VRT. You can now run the final command, `create-xyz`!')

        proceed(createXYZ)

    return

#########################################
#####                               #####
#####       STEP 5: `createXYZ`     #####
#####         to create final       #####
#####           XYZ tileset         #####
#####                               #####
#########################################

def createXYZ():
    
    path="./"
    cmd = [
        "gdal2tiles.py", "--xyz", "-z", "13-20", "--exclude", "--processes", "4", "tmp/mosaic.vrt", "output/tiles"
    ]

    print("Beginning to generate XYZ tiles...")
    subprocess.run(
        cmd,
        cwd=path
    )

    print('🎉 XYZ tiles have been created. All files are in the `output` directory, ready to be ingested into Atlascope!')

    return

#########################################
#####                               #####
#####    STEP 6: `writeToExtents`   #####
#####     to update extent file     #####
#####       in metadata repo        #####
#####                               #####
#########################################

def writeToExtents(url):

    # we'll load from and write to this path -- be careful!
    # because this is our GitHub repository,
    # changes can be rolled back by discarding from git/GitHub Desktop

    extentsPath="/Users/geoprocessing/Documents/GitHub/lmec-digital-library-metadata/atlascope/atlascope-boston/boston-volume-extents.geojson"

    with open(extentsPath) as f:
        data = json.load(f)

    template=copy.deepcopy(data['features'][0])
    data['features'].insert(0,template)

    # update properties

    with open('output/tileset.json') as f:
        tileset = json.load(f)

    newAtlas=data['features'][0]['properties']

    newAtlas['identifier'] = f"ark:/76611/{tileset['tiles'][0][48:57]}"
    newAtlas['publisherShort'] = tileset['description'][tileset['description'].find("(")+1:-7]
    newAtlas['year'] = tileset['description'][-5:-1]
    newAtlas['bibliographicEntry'] = f"_{tileset['description'].split("(")[0].strip()}_ ({tileset['description'].split("(")[1]}"
    newAtlas['source'] = { "type": "tilejson", "url": f"https://s3.us-east-2.wasabisys.com/urbanatlases/{tileset['tiles'][0][48:57]}/tileset.json"}
    newAtlas['catalogPermalink'] = f"https://collections.leventhalmap.org/search/{url}"
    newAtlas['heldBy'] = [ "" ]
    newAtlas['sponsors'] = [ "" ]

    # update geometry

    with open('tmp/plates-precise.geojson') as f:
        d = json.load(f)
        geom=d['features'][0]['geometry']

    data['features'][0]['geometry'] = geom

    with open(extentsPath, "w") as f:
        json.dump(data, f)

#########################################
#####                               #####
#####    STEP 7: `writeToWasabi`    #####
#####    to copy `output` contents  #####
#####       to Wasabi bucket        #####
#####                               #####
#########################################

def writeToWasabi():

    id=os.getcwd()[os.getcwd().find("atlases/"):].replace("atlases/","").strip()

    os.environ["AWS_MAX_CONCURRENT_REQUESTS"] = "20"
    os.environ["AWS_S3_MAX_CONCURRENT_REQUESTS"] = "20"

    cmd = [
        "aws", "s3", "sync",
        "output/",
        f"s3://urbanatlases/{id}/",
        "--endpoint-url", "https://s3.us-east-2.wasabisys.com",
        "--region", "us-east-2",
    ]

    subprocess.run(cmd, check=True)


#########################################
#####                               #####
#####  `createDirectoryStructure`   #####
#####   is run at every step to     #####
#####    avoid funny business       #####
#####                               #####
#########################################

def createDirectoryStructure():
    d = os.path.exists
    if not d('./tmp'):
        os.mkdir('./tmp')
    if not d('./tmp/img'):
        os.mkdir('./tmp/img')
    if not d('./tmp/annotations'):
        os.mkdir('./tmp/annotations')
    if not d('./tmp/warped'):
        os.mkdir('./tmp/warped')
    if not d('./output'):
        os.mkdir('./output')
    if not d('./tmp/annotations/transformed'):
        os.mkdir('./tmp/annotations/transformed') 

#########################################
#####                               #####
#####     define which functions    #####
#####       are associated with     #####
#####          which step           #####
#####                               #####
#########################################

if __name__ == "__main__":
        
    # no matter what step we're running
    # first run the directory structure function
    # to ensure that the right subdirectories exist

    createDirectoryStructure()

    if args.step == 'download-inputs':
        downloadInputs(args.identifier)
    elif args.step == 'allmaps-transform':
        allmapsTransform(args.identifier)
    elif args.step == 'warp-plates':
        warpPlates()
    elif args.step == 'mosaic-plates':
        mosaicPlates()
    elif args.step =='create-xyz':
        createXYZ()
    elif args.step =='write-extents':
        writeToExtents(args.identifier)
    elif args.step =='write-wasabi':
        writeToWasabi()
    else:
        print("ERROR: Step not recognized")