# Dependent libralies
    face_recognition
    opencv
    numpy
    dlib

# use cnn to acceralate this
     wget http://dlib.net/files/dlib-19.21.tar.bz2
     tar jxvf dlib-19.21.tar.bz2
     cd dlib-19.21/
     mkdir build
     cd build/
     cmake ..
     cmake --build .
     cd ../
     sudo python3 setup.py install
    #python3
     sudo python3 -m pip install face_recognition
    #python2
     sudo python -m pip install face_recognition
