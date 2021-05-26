import os

start_dir = os.getcwd()

# mahimahi
os.system("sudo sysctl -w net.ipv4.ip_forward=1")
os.system("sudo apt-get -y update")

# apache server
# os.system("sudo apt-get -y install apache2")

# selenium
os.system("wget 'https://pypi.python.org/packages/source/s/selenium/selenium-2.39.0.tar.gz'")
os.system("sudo apt-get -y install python-setuptools python-pip xvfb xserver-xephyr tightvncserver unzip")
os.system("tar xvzf selenium-2.39.0.tar.gz")
selenium_dir = start_dir + "/selenium-2.39.0"
os.chdir( selenium_dir )
os.system("sudo python setup.py install" )
os.system("sudo sh -c \"echo 'DBUS_SESSION_BUS_ADDRESS=/dev/null' > /etc/init.d/selenium\"")

# py virtual display
os.chdir( start_dir )
os.system("sudo pip install pyvirtualdisplay==1.3.2")
os.system("wget 'https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb' ")
os.system("sudo dpkg -i google-chrome-stable_current_amd64.deb")
os.system("sudo apt-get -f -y install")

# tensorflow
os.system("sudo apt-get -y install python-pip python-dev")
os.system("sudo pip install tensorflow")

# tflearn
os.system("sudo pip install tflearn")
os.system("sudo apt-get -y install python-h5py")
os.system("sudo apt-get -y install python-scipy")

# matplotlib
os.system("sudo apt-get -y install python-matplotlib")

os.chdir( start_dir )

# make results directory
# os.system("mkdir rl_server/results")
os.system("mkdir run_exp/bw_prediction")
os.system("mkdir run_exp/bw_truth")
os.system("mkdir run_exp/results")
os.system("mkdir run_exp/results_driving")
os.system("mkdir run_exp/results_walking")
os.system("mkdir run_exp/results_interface_sel")
os.system("mkdir run_exp/results_predict")
os.system("mkdir run_exp/results_chunk_length")

# need to copy the trace and pre-trained NN model
print "Finished"
