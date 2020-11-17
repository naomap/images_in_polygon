# images_in_polygon
```
usage: images_in_poly.py [-h] [-v] -j JSON_FILE -s SOURCE [-d DESTINATION]

Script to find in which polygon a geolocalized image belongs to

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -j JSON_FILE, --json_file JSON_FILE
                        Path to the geojson file
  -s SOURCE, --source SOURCE
                        Path to the images folder. Sub folder are scanned too
  -d DESTINATION, --destination DESTINATION
                        Path to the destination folder in which the images
                        will be copied
                        
```
                        
## installation:

+ Create a virtual environnement: `python3 -m venv image_in_polygon`
+ Move to this environnement: `cd image_in_polygon`
+ Activate this environnement: `source bin/activate`
+ Clone this repository: `git clone https://github.com/Stefal/images_in_polygon.git`
+ Install the requirements: `pip install -r images_in_polygon/requirements.txt`
