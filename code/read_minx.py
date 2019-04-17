import os
import re
import json
import sys
import numpy as np

PLUME_RE = "Plumes_O\d+\-[B]\d+\-[SPWBR]\d+\.txt"
# PLUME_RE = "Plumes_O*.txt"
FILL_VALUE = -999.99

FILLS = [-9.999, -99, -99.9, -999.9]

def parsePlumeTxtFull(fpaths):
    outArr = []

    for f in fpaths:
        if os.path.isfile(f):

            case = {}
            
            with open(f, 'r') as fstream:
            
                #Header

                case["orbit"] = (int)((fstream.readline().split())[3])
                case["path"] = (int)((fstream.readline().split())[3])
                case["block"] = (int)((fstream.readline().split())[3])

                case["date"] = ((fstream.readline().split())[3])
                case["time_UTC"] = ((fstream.readline().split())[3])
                # case["minx_version"] = ((fstream.readline().split())[3])
                #MISR file info, blank lines, etc.
                for i in range(0, 4):
                    fstream.readline()

                case["region"] = (fstream.readline().split())[3]
                case["aerosol_type"] = (fstream.readline().split())[4]
                case["geometry_type"] = (fstream.readline().split())[4]

                #Region wind dir type, retrieved w/ band, retrieved w/ matcher, retrieved w/ cams, retrieval precision
                for i in range(0, 5):
                    fstream.readline()
                    
                case["min_height"] = (float)((fstream.readline().split())[6])
                case["max_height"] = (float)((fstream.readline().split())[6])
                case["sample_spacing"] = (float)((fstream.readline().split())[4])
                 
				#Registration corrected, Image color equalized, empty, first point lat/lon, geographic region
                for i in range(0, 6):
                	fstream.readline()

                biome_line = fstream.readline().split()	
                # case["biome_name"] = biome_line[5]
                case["biome_name"] = biome_line[5] if len(biome_line) == 7 else biome_line[5]+' '+biome_line[6]
                case["biome_id"]  = int(biome_line[len(biome_line)-1])

                #Red/Blue band better?
                fstream.readline()

                case["perimeter_km"] = (int)((fstream.readline().split())[4])
                case["area_sq_km"] = (int)((fstream.readline().split())[4])
                case["per_point_area_sq_km"]  = (float)((fstream.readline().split())[6])
                

                #Num. heights retrieved
                fstream.readline()

                #case["wind_corrected_count"] = (int)((fstream.readline().split())[3])
                case["percent_area_covered"] = (int)((fstream.readline().split())[4])
                case["fire_elevation"] = (int)((fstream.readline().split())[6])
                case["best_median_height_m"] = (int)((fstream.readline().split())[6])
                case["best_top_heigh_m"] = (int)((fstream.readline().split())[6])
                case["height_st_dev"] = (int)((fstream.readline().split())[5])
                case["height_local_var"] = (int)((fstream.readline().split())[5])
                #case["corrht"] = (int)((fstream.readline().split())[4])
                case["diff_dir_wind_at"] = (int)((fstream.readline().split())[2])
                case["fire_power_mw"] = (float)((fstream.readline().split())[5])
                case["quality"] = (fstream.readline().split())[4]
                
                #pyro-cumulus, comments, empty
                for i in range(0, 3):
                    fstream.readline()

                case["l1_rad_file"] = (fstream.readline().split())[5]
                case["terrain_elevation_file"] = (fstream.readline().split())[4]
                case["geometry_file"] = (fstream.readline().split())[4]
                case["classifier_file"] = (fstream.readline().split())[4]
                case["aerosol_file"] = (fstream.readline().split())[4]
                case["biome_file"] = (fstream.readline().split())[5]	

                #empty
                fstream.readline()
                     
                #Polygon
                poly_pts = (int)((fstream.readline().split())[1])

                #Polygon Header
                for i in range(0, 3):
                	fstream.readline()

                case["polygon"] = {"lat":[], "lon":[], "line":[], "sample":[], "block":[]}

                #Polygon Table
                for i in range(0, poly_pts):
                    line = fstream.readline().split()
                    case["polygon"]["lon"].append((float)(line[1]))
                    case["polygon"]["lat"].append((float)(line[2]))
                    case["polygon"]["block"].append((int)(line[3]))
                    case["polygon"]["sample"].append((int)(line[4]))
                    case["polygon"]["line"].append((int)(line[5]))	

                #empty
                fstream.readline() 

                #Direction
                dir_pts = (int)((fstream.readline().split())[1])

                case["direction"] = {"lat":[], "lon":[], "line":[], "sample":[], "block":[]}

                #Direction Header
                for i in range(0, 3):
                    fstream.readline()

                #Direction Table	
                for i in range(0, dir_pts):
                    line = fstream.readline().split()
                    case["direction"]["lon"].append((float)(line[1]))
                    case["direction"]["lat"].append((float)(line[2]))
                    case["direction"]["block"].append((int)(line[3]))
                    case["direction"]["sample"].append((int)(line[4]))
                    case["direction"]["line"].append((int)(line[5]))


                #empty
                fstream.readline()

                #Results
                count = (int)((fstream.readline().split())[1])

                case["image_location"] = {"line":[], "sample":[], "block":[]}
                case["position"] = {"lat":[], "lon":[], "clockwise_direction_from_north":[], "terrain_elevation":[], "distance_from_pt1_km":[]}
                case["feature_height_m"] = {"wind_corrected":[], "zero_wind":[], "wind_filtered":[], "fill":-9999}
                case["wind_speed"] = {"across_track": [], "along_track": [], "total":[], "fill":-99.9}
                case["optical_depth"] = {"red": [], "green": [], "blue": [], "nir": [], "fill":-9.999}
                case["single_scattering_albedo"] = {"red": [], "green": [], "blue": [], "nir": [], "fill":-9.999}	
                case["tau_frac"] = {"small_part":[], "med_part":[], "large_part":[], "sphere_part":[], "fill":-9.999}
                case["power_mw"] = {"data":[], "fill":-99.9}
                case["angstrom"] = {"data":[], "fill":-9.999}
                

                #table header
                for i in range(0, 3):
                    fstream.readline()

                #Results Table
                for i in range(0, count):
                    line = fstream.readline().split()

                    case["position"]["lon"].append((float)(line[1]))
                    case["position"]["lat"].append((float)(line[2]))
                    case["position"]["distance_from_pt1_km"].append((float)(line[6]))
                    case["position"]["clockwise_direction_from_north"].append((int)(line[7]))
                    case["position"]["terrain_elevation"].append((int)(line[8]))

                    case["image_location"]["block"].append((int)(line[3]))
                    case["image_location"]["sample"].append((int)(line[4]))
                    case["image_location"]["line"].append((int)(line[5]))

                    case["feature_height_m"]["zero_wind"].append(checkFill((int)(line[9]), case["feature_height_m"]["fill"]))
                    case["feature_height_m"]["wind_corrected"].append(checkFill((int)(line[10]), case["feature_height_m"]["fill"]))
                    case["feature_height_m"]["wind_filtered"].append(checkFill((int)(line[11]), case["feature_height_m"]["fill"]))

                    case["wind_speed"]["across_track"].append(checkFill((float)(line[12]), case["wind_speed"]["fill"]))
                    case["wind_speed"]["along_track"].append(checkFill((float)(line[13]), case["wind_speed"]["fill"]))
                    case["wind_speed"]["total"].append(checkFill((float)(line[14]), case["wind_speed"]["fill"]))

                    case["optical_depth"]["blue"].append(checkFill((float)(line[15]), case["optical_depth"]["fill"]))
                    case["optical_depth"]["green"].append(checkFill((float)(line[16]), case["optical_depth"]["fill"]))
                    case["optical_depth"]["red"].append(checkFill((float)(line[17]), case["optical_depth"]["fill"]))
                    case["optical_depth"]["nir"].append(checkFill((float)(line[18]), case["optical_depth"]["fill"]))

                    case["single_scattering_albedo"]["blue"].append(checkFill((float)(line[19]), case["single_scattering_albedo"]["fill"]))
                    case["single_scattering_albedo"]["green"].append(checkFill((float)(line[20]), case["single_scattering_albedo"]["fill"]))
                    case["single_scattering_albedo"]["red"].append(checkFill((float)(line[21]), case["single_scattering_albedo"]["fill"]))
                    case["single_scattering_albedo"]["nir"].append(checkFill((float)(line[22]), case["single_scattering_albedo"]["fill"]))
                    
                    case["tau_frac"]["small_part"].append(checkFill((float)(line[23]), case["tau_frac"]["fill"]))
                    case["tau_frac"]["med_part"].append(checkFill((float)(line[24]), case["tau_frac"]["fill"]))
                    case["tau_frac"]["large_part"].append(checkFill((float)(line[25]), case["tau_frac"]["fill"]))
                    case["tau_frac"]["sphere_part"].append(checkFill((float)(line[26]), case["tau_frac"]["fill"]))

                    case["angstrom"]["data"].append(checkFill((float)(line[27]), case["angstrom"]["fill"]))

                    case["power_mw"]["data"].append(checkFill((float)(line[28]), case["power_mw"]["fill"]))

                    #case["reflectance"]["data"].append(checkFill((float)(line[29]), case["reflectance"]["fill"]))
                    
                    #case["brightness_temps_k"]["21"].append(checkFill((float)(line[33])))
                    #case["brightness_temps_k"]["31"].append(checkFill((float)(line[34])))
                    #case["brightness_temps_k"]["21BB"].append(checkFill((float)(line[35])))
                    #case["brightness_temps_k"]["31BB"].append(checkFill((float)(line[36])))




            outArr.append(case)

    return outArr

def parsePlumeTextDemo(fpaths):

    outArr = []

    for f in fpaths:
        if os.path.isfile(f):

            case = {}
            uid = 0

            with open(f, 'r') as fstream:
                for i in range(0, 3):
                    fstream.readline()

                case["id"] = uid
                uid += 1

                case["date"] = ((fstream.readline().split())[3])
                case["time_UTC"] = ((fstream.readline().split())[3])

                                #MISR file info, blank lines, etc.
                for i in range(0, 17):
                    fstream.readline()

                count = (int)((fstream.readline().split())[5])

                for i in range(0, 11):
                    fstream.readline()


                case["lat"] = []
                case["lon"] = []
                case["terrain_elevation"] = []
                case["plume_height"] = []
                case["aerosol_optical_depth_green"] = []
                case["power_mw"] = []
                case["wind_azimuth"] = []
                case["wind_speed_x"] = []
                case["wind_speed_y"] = []

                for i in range(0, count):
                    line = fstream.readline().split()

                    case["lon"].append((float)(line[1]))
                    case["lat"].append((float)(line[2]))
                                        
                    case["wind_azimuth"].append((int)(line[7]))

                    case["terrain_elevation"].append((int)(line[8]))
                    #TODO checkFIll
                    if line[10] == "-99":
                        if line[9] == "-99":
                            case["plume_height"].append(FILL_VALUE)
                        else:
                            case["plume_height"].append((int)(line[9]))
                    else:
                        case["plume_height"].append((int)(line[10]))

                    if line[11] == "-99.9":
                        case["wind_speed_x"].append(FILL_VALUE)
                    else:
                        case["wind_speed_x"].append(abs((float)(line[11])))

                    if line[12] == "-99.9":
                        case["wind_speed_y"].append(FILL_VALUE)
                    else:
                        case["wind_speed_y"].append((float)(line[12]))

                    if line[19] == "-9.999":
                        case["aerosol_optical_depth_green"].append(FILL_VALUE)
                    else:
                        case["aerosol_optical_depth_green"].append((float)(line[19]))

                    if line[31] == "-99.9":
                        case["power_mw"].append(FILL_VALUE)
                    else:
                        case["power_mw"].append((float)(line[31]))


                outArr.append(case)
    return outArr



def findFiles(dr):

    ret = []

    if os.path.isdir(dr):
        for root, dirs, files in os.walk(dr):
            for fle in files:
            	# if re.match(PLUME_RE, fle):
            	ret.append(os.path.join(root, fle))
            	print(fle)
    return ret


#TODO fix up
def formatForML(case):
    out = {"lat":[], "lon":[], "features":[]}
    out["lat"] = np.array(case["position"]["lat"])
    out["lon"] = np.array(case["position"]["lon"])

    outFeat = []
    for i in range(0, len(case["feature_height_m"]["wind_corrected"])):
        dataPt = []
        if case["feature_height_m"]["wind_corrected"][i] == FILL_VALUE:
            dataPt.append(case["feature_height_m"]["zero_wind"][i])
        else:
            dataPt.append(case["feature_height_m"]["wind_corrected"][i])

        #dataPt.append(case["position"]["distance_from_pt1_km"][i])
        #dataPt.append(case["position"]["clockwise_direction_from_north"][i])
        dataPt.append(case["position"]["terrain_elevation"][i])
    
        #dataPt.append(case["wind_speed"]["across_track"][i])
        #dataPt.append(case["wind_speed"]["along_track"][i])
        #dataPt.append(case["albedo"]["red"][i])
        #dataPt.append(case["albedo"]["green"][i])
        #dataPt.append(case["albedo"]["blue"][i])
        #dataPt.append(case["albedo"]["nir"][i])
        #dataPt.append(case["albedo"]["top_of_atmosphere"][i])
        #dataPt.append(case["single_scattering_albedo"]["red"][i])
        #dataPt.append(case["single_scattering_albedo"]["green"][i])
        #dataPt.append(case["single_scattering_albedo"]["blue"][i])
        #dataPt.append(case["single_scattering_albedo"]["nir"][i])
        #dataPt.append(case["optical_depth"]["red"][i])
        dataPt.append(case["optical_depth"]["green"][i])
        #dataPt.append(case["optical_depth"]["blue"][i])
        #dataPt.append(case["optical_depth"]["nir"][i])
        #dataPt.append(case["tau_frac"]["small_part"][i])
        #dataPt.append(case["tau_frac"]["med_part"][i])
        #dataPt.append(case["tau_frac"]["large_part"][i])
        #dataPt.append(case["tau_frac"]["sphere_part"][i])
        dataPt.append(case["power_mw"]["data"][i])
        #dataPt.append(case["reflectance"]["data"][i])
        #dataPt.append(case["angstrom"]["data"][i])
        #dataPt.append(case["brightness_temps_k"]["21"][i])
        #dataPt.append(case["brightness_temps_k"]["31"][i])
        #dataPt.append(case["brightness_temps_k"]["21BB"][i])
        #dataPt.append(case["brightness_temps_k"]["31BB"][i])


        outFeat.append(dataPt)
    print(len(outFeat), len(outFeat[0]))
    out["features"] = np.array(outFeat)
    print(out["features"].shape, out["lat"].shape, out["lon"].shape)

    return out


def parsePlumeFiles(files, outFile, full = True):
    dct = {}
    if full:
        dct = parsePlumeTxtFull(files)
    else:
        dct = parsePlumeTextDemo(files)

    output = json.dumps(dct)

    with open(outFile, 'w') as jFile:
        jFile.write(output)

    return dct


def parsePlumeDir(dr, outFile, full = True):
    files = findFiles(dr)
    print(files)
    dct = parsePlumeFiles(files, outFile, full)
    return dct

def checkFill(value, fill):
    if value == fill and value in FILLS:
        return FILL_VALUE
    return value


if __name__ == '__main__':
	PATH = "../data/plume_dataset/"
	
	# PATH = '../data/'
	plumeDir = PATH + sys.argv[1]
	outFile = PATH + sys.argv[2]
	parseFullStr = sys.argv[3]
	parseFull = False

	print(plumeDir)
	print(outFile)
	print(parseFullStr)

	if parseFullStr.lower() == 'true':
 		parseFull = True
	parsePlumeDir(plumeDir, outFile, parseFull)

#parsePlumeDir("/Users/nlahaye/Desktop/VR/data/California2008/SoCalCase", "/Users/nlahaye/Desktop/VR/Plume_VR_Demo_Southern_Ca_2008.json", False)


# TO RUN: python read_minx.py test plume_test.json true


