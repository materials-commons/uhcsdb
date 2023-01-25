# [UHCSDB dataset explorer](http://uhcsdb.materials.cmu.edu)
A dynamic microstructure exploration application built on Flask and Bokeh.

Run flask app uhcsdb/uhcsdb.py in parallel with bokeh app uhcsdb/visualize.py

The Ultrahigh Carbon Steel (UHCS) microstructure dataset is available on [materialsdata.nist.gov](https://hdl.handle.net/11256/940) ([https://hdl.handle.net/11256/940)](https://hdl.handle.net/11256/940).

---
**NOTE: The original link (given above) appears broken. The dataset can be found on [materialsdata.nist.gov](https://materialsdata.nist.gov/handle/11256/940) ([https://materialsdata.nist.gov/handle/11256/940)](https://materialsdata.nist.gov/handle/11256/940)**


Please cite use of the UHCS microstructure data as:
```TeX
@misc{uhcsdata,
  title={Ultrahigh Carbon Steel Micrographs},
  author={Hecht, Matthew D. and DeCost, Brian L. and Francis, Toby and Holm, Elizabeth A. and Picard, Yoosuf N. and Webler, Bryan A.},
  howpublished={\url{https://hdl.handle.net/11256/940}}
}
```

The UHCS dataset is documented by a data descriptor published in *Integrating Materials and Manufacturing Innovation* (doi: [10.1007/s40192-017-0097-0](https://dx.doi.org/10.1007/s40192-017-0097-0)).
You can find our preprint version of the accepted manuscript [here (pdf)](https://holmgroup.github.io/publications/uhcs-data.pdf).
For work that builds on these data visualization tools, please cite our forthcoming IMMI manuscript:
```TeX
@article{uhcsimmi,
  title={UHCSDB (Ultrahigh Carbon Steel micrograph DataBase): tools for exploring large heterogeneous microstructure datasets},
  author={DeCost, Brian L. and Hecht, Matthew D. and Francis, Toby  and Webler, Bryan A. and Picard, Yoosuf N. and Holm, Elizabeth A.},
  year={2017},
  journal={Accepted for publication in IMMI},
  doi={10.1007/s40192-017-0097-0}
}
```

## Check out the data

```sh
git clone https://github.com/materials-commons/uhcsdb.git
cd uhcsdb
```

All of the data is hosted on the NIST repository [https://materialsdata.nist.gov/handle/11256/940](https://materialsdata.nist.gov/handle/11256/940). If the links break, the repository can most likely be found by googling "Ultrahigh Carbon Steel Micrographs NIST"

## Download the appropriate files accordlingly:
- Store microtructure metadata (`microstuctures.sqlite`) in `uhcsdb/microstructures.sqlite`
- Store (unzip) image files (`micrographs.zip`) under `uhcsdb/static/micrographs`.
- Store (unzip) image representations (`representations.zip`) in HDF5 under `uhcsdb/static/representations`.
- Store (unzip) reduced-dimensionality representations (`embed.zip`) in HDF5 under `uhcsdb/static/embed`.

## Process images and thumbnails for webapp integration
- Store (& unzip) `tools.zip` in top level directory, i.e. 
  ```sh
  cd ../
  ```
- Convert fullsized images to .png for browser compatibility
  ```sh
  bash tools/convert_to_png.sh
  ```
- Make thumbnails for dataviz app
  ```sh
  bash tools/make_thumbs.sh
  ```

## Launch app
```sh
cd uhcsdb
bash uhcsdb/launch.sh
```





