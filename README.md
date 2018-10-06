# low-poly-painter
## Requirements
* **Python2.7**
* **Python packages:**
    * Numpy
	* Tkinter (Should be installed by default)
	* Pillow (or other PIL versions)
	* Scipy
	* SVGwrite
	* OpenCV
	* Scikit-image

## Recommended
* **VirtualEnv:** A python tool to create separate environments with different python versions and packages.

## How to run
1. Clone the repository
2. **Optional:** Create a new virtual environment in this folder, e.g.  
`virtualenv --python=D:\Python27\python.exe env`  
(Use `source env/bin/activate` or deactivate to enable/disable this virtualEnv)
3. `pip install numpy scipy pillow svgwrite opencv-python bresenham scikit-image tkcolorpicker enum34`
4. Change to cloned directory  
5. Run the program: `python lowpolypainter.py lenna.jpg`
