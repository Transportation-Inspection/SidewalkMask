# SidewalkMask

Masks of sidewalks are generated for google map satellite images, based on overlapping the sidewalk shapefile on top.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 

### Prerequisites
Install [python](https://www.python.org/downloads/).
The code is in python3.x. If you are using python2.x, you will need a [3to2](https://pypi.python.org/pypi/3to2) package to convert the code into python2 syntax. Download and install 3to2 package. Run with -w flag to convert and backup original files(.bak).
```
sudo python setup.py build
sudo python setup.py install
3to2 files -w path/to/your/filename.py
```

It's also recommended to install:
* [QGIS Desktop](http://www.qgis.org/en/site/forusers/download.html).
* [Virtualenv](https://virtualenv.pypa.io/en/stable/) for python.


### Installing
##### Start Virtualenv
It's recommended (optional) to run your program in virtualenv:
```
virtualenv -p /usr/bin/python3 py3env-sidewalk
source py3env-sidewalk/bin/activate
```
##### Install python packages
Browse to SidewalkMask directory, install all packages with pip:
```
 $ sudo apt-get install python3-pip
 $ pip3 install -w requirements.txt
```
Congratulations you are ready to go!!
If you runs into error, fix the error and rerun the command above.
**Example errors:**
1.Missing modules.
```
 $ pip3 install psycopg2
 $ pip3 install typing 
 $ pip3 install Cython
```
2.Uable to install rtree in lack of libspatialindex.
For libspatialindex package, download and make install. run `sudo ldconfig`. Then install rtree either with requirements.txt or from .whl.
3.Error: /usr/bin/ld: cannot find -lopenblas
The reason is missing library: `sudo apt-get install libopenblas-dev`
4.Last tip: If you have error installing one package, maybe try to remove it
from the requirements.txt and install the rest first.
##### Create Postgres database
We use [postgres](https://www.postgresql.org/download/) and postgis as the database. 
```
$ sudo apt-get update
$ sudo apt-get install postgresql postgresql-contrib
```
Now test if postgres exist: `ls -l /etc/init.d/post*` which shows `postgresql`
Now you can start the server `sudo service postgresql start`
Note, if `ls` command returns `postgres`, then start server using `sudo service postgres start` It depends on what name your machine refers to the server.
Next, install postgis.
```
$ sudo apt-get install -y postgis postgresql-9.3-postgis-2.11
```
Log into the initial account with default user: `sudo -i -u postgres`. Then,
```
$ createdb sidewalk_dataset
$ psql sidewalk_dataset
sidewalk_dataset# CREATE USER sidewalk WITH PASSWORD 'sidewalk';
sidewalk_dataset# GRANT ALL PRIVILEGES ON DATABASE sidewalk_dataset TO sidewalk;
sidewalk_dataset# \q
```
Now create postgis extension for your database.
```
sudo -u postgres psql -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;" sidewalk_dataset
```
##### Create Schema in sidewalk_dataset
Connect to sidewalk_dataset with `psql sidewalk_dataset`.
```
sidewalk_dataset=# CREATE SCHEMA sidewalk;
sidewalk_dataset=# ALTER SCHEMA sidewalk OWNER TO sidewalk;
sidewalk_dataset=# SET search_path TO <yourschema>, public, pg_catalog, topology;
```
If the spatial reference system is not listed in public.spatial_ref_sys, write them in a csv file and import :
```
sidewalk_dataset=#  COPY spatial_ref_sys FROM '/home/pothole/Downloads/spatial_ref_sys.csv' DELIMITER ',' CSV HEADER;
```

##### Export shapefile into .sql
First, decide SRID using this [website](http://prj2epsg.org/search) by uploading the .prj file. For GCS_WGS_1984, the SRID is 4326. Now convert your shapefile into .sql file. `shp2pgsql -s <SRID> <shapefile> <schema>.<tablename> <db_name> > filename.sql`

``` 
$ shp2pgsql -s 4326 /media/pothole/TOSHIBA/DC_roads_all/Roads_All.shp dc.sidewalk_test sidewalk_dataset > sidewalk_test.sql
$ sudo -u sidewalk psql -d sidewalk_dataset -a -f filename.sql
```
If succeeded, you should see the tablename in your database.
```
sidewalk_dataset=# \dt
               List of relations
  Schema  |      Name       | Type  |  Owner
----------+-----------------+-------+----------
 public   | spatial_ref_sys | table | postgres
 topology | layer           | table | postgres
 topology | topology        | table | postgres
(3 rows)

sidewalk_dataset=# \dn
   List of schemas
   Name   |  Owner
----------+----------
 dc       | sidewalk
 public   | postgres
 sidewalk | sidewalk
 topology | postgres
(4 rows)

sidewalk_dataset=# \l
                                     List of databases
       Name       |  Owner   | Encoding |   Collate   |    Ctype    |   Access privileges
------------------+----------+----------+-------------+-------------+-----------------------
 postgres         | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 |
 sidewalk         | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 |
 sidewalk_dataset | sidewalk | UTF8     | en_US.UTF-8 | en_US.UTF-8 | =Tc/sidewalk         +
                  |          |          |             |             | sidewalk=CTc/sidewalk
 template0        | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 | =c/postgres          +
                  |          |          |             |             | postgres=CTc/postgres
 template1        | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 | =c/postgres          +
                  |          |          |             |             | postgres=CTc/postgres
(5 rows)

```
##### Export pgsql to shapefile:
`pgsql2shp -f "sidewalk_polygon" -h localhost -u sidewalk -P sidewalk sidewalk_dataset dc.sidewalk_polygon` to virualize and verify the data.

## Running the code
Create your own API KEY to access the google satellite images [here](https://developers.google.com/maps/documentation/static-maps/get-api-key).
Paste in to the script.
```
$ python3 src/download_google_map.py
$ python3 src/GoogleStaticMapMasks.py
```
You will find the output under data/output folder.
