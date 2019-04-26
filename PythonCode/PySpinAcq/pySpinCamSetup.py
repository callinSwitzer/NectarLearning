import PySpin

def comConnect():
	# check number of cameras
	system = PySpin.System.GetInstance()

	# Retrieve list of cameras from the system
	cam_list = system.GetCameras()
	numCams = cam_list.GetSize()


	print("Number of cameras detected: ", numCams)

	if not numCams:
		#raise ValueError("Insufficient number of cameras. Exiting...")
		print("Insufficient number of cameras. Exiting...")
		exit()

	for i, cam in enumerate(cam_list):
		# Retrieve TL device nodemap
		nodemap_tldevice = cam.GetTLDeviceNodeMap()


		# Initialize camera
		cam.Init()
		print("Camera " + str(i) + " connected")
		

		node_acquisition_mode = PySpin.CEnumerationPtr(cam.GetNodeMap().GetNode('AcquisitionMode'))

        # Set acquisition mode to continuous
		if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
			print('Unable to set acquisition mode to continuous (node retrieval; camera %d). Aborting... \n' % i)
			return(False)
		
		node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
        
		if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(node_acquisition_mode_continuous):
			print('Unable to set acquisition mode to continuous... Aborting... \n')
			return(False)
		
		acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

		node_acquisition_mode.SetIntValue(acquisition_mode_continuous)
		print("Camera " + str(i) + " acquisition mode set to continuous")

		# cam.BeginAcquisition()
		# print("Camera streaming started")
	# return(cam_list)


def getImage():
	image_result = []
	for i, cam in enumerate(cam_list):
		image_result.append(cam.GetNextImage())
	print("got images from both cameras")
	
	for cam in cam_list:
		# End acquisition
		cam.EndAcquisition()
	return(image_result)


def main():
	cam_list = comConnect()
	imgs = getImage(cam_list)

