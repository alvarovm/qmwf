import subprocess, os
from external_libs import bgqtools
import time
import multiprocessing


import sys
import signal
import functools

src_dir = os.getcwd()
config = {}

SIGNALS = {
    signal.SIGINT: 'SIGINT',
    signal.SIGTERM: 'SIGTERM',
}

def receive_signal(processes, signum, stack):
    print('\n nwchemnw received SIGNAL: %s \n' % signum)
    if len(processes) != 0 :
        print('nwchemnw killing subprocesses')
        for p in processes:
            p.terminate()
        time.sleep(50)
    else:
        print("processes list is empty")

def main():
        launch_parallel()

def launch_parallel(config):
    try:
        parallelization_method = config['parallelization_method']
        if parallelization_method == "subprocess":
            #launch_parallel_subprocess()
            return
        elif parallelization_method == "mira" or parallelization_method == "cetus" or parallelization_method == "vesta":
            launch_parallel_bgq(config)
            return
        else:
            raise ValueError("Unknown parallelization method: "+parallelization_method)
    except ValueError:
        print ("no parallelization_method")
        return


def launch_parallel_bgq(config):
        '''
        Launches new replicas using subprocessing
        with each replica assigned an appropriate block and corner
        on ALCF's Mira and Cetus machine

	launch_parallel_bgq -> corners, shape, launch-> serial
        '''
        nodes_per_replica = config['nodes_per_replica']
        bgq_block_size = config['bgq_block_size']
        parallelization_method = config['parallelization_method']
        ranks_per_node =  config['ranks_per_node']
        #python_command = config['python_command']
        python_command = sys.executable
        comm = config['callscript']
        binary = config['binary']

        npr = nodes_per_replica
        if bgq_block_size:
                block_size = bgq_block_size
                if parallelization_method == "mira" and block_size < 512:
                        message = "bgq_block_size specified as %i\n" % (block_size)
                        message+= "On mira, a block is at least 512 nodes!"
                        raise ValueError(message)
        else:
                if parallelization_method == "mira":
                        block_size = 512
                if parallelization_method == "vesta":
                        block_size = 32
                else: #Cetus
                        block_size = 128


        partsize, partition, job_id = bgqtools.get_cobalt_info()
        print partsize, partition, job_id
        if block_size > partsize:
                message = "block size larger than the total number of nodes; "
                message += "modify bgq_block_size or submission script"
                raise ValueError(message)
        if npr > block_size:
                message = "Number of nodes per replica (%i) " % npr
                message += "larger than block size (%i); " % block_size
                message += "Modify nodes_per_replica or bgq_block_size"
                raise ValueError(message)

        blocks = bgqtools.get_bootable_blocks(partition, partsize, block_size)
        print blocks
        bgqtools.boot_blocks(blocks)
        corners = bgqtools.block_corner_iter(blocks, npr)

        print corners

        processes = []
        handler = functools.partial(receive_signal, processes)
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)

        print ("launcher My PID is: %s \n" % os.getpid())

        logfile_path = os.path.join(src_dir,'log')
        try:
            os.mkdir(logfile_path)
        except:
            print("%s dir is in place" % logfile_path)
        #comm = './callnwbg_pre_master.py'

##debug        print 'caca0011'
##debug        print corners
        for corner in corners:
                runjob_block = corner[0]
                runjob_corner = corner[1]
                runjob_shape = corner[2]
                runjob_modes = ranks_per_node
     ########### RUN SOMETHIG
##debug        arglist = [python_command,comm,
##debug                "binary="+str(binary)]
##debug        p = subprocess.Popen(arglist)
##debug        processes.append(p)
##debug        p.wait()
                arglist = [python_command, comm,
                "block="+ str(runjob_block),
                "corner="+ str(runjob_corner),
                "shape="+ str(runjob_shape),
                "modes="+ str(runjob_modes),
                "nodes_per_replica="+ str(nodes_per_replica),
                "binary="+str(binary)]
                             #"fileconfig="+str(os.path.join(src_dir,config['fileconfig']))]
##debug                print arglist
                logfile = os.path.join(logfile_path,"nwchem_log"+str(runjob_block)+str(runjob_corner)+str(runjob_shape)+str(job_id))
                errfile = os.path.join(logfile_path,"nwchem_err"+str(runjob_block)+str(runjob_corner)+str(runjob_shape)+str(job_id))
                outputlog = outfile = open(logfile,"w")
                outputerr = outfile = open(errfile,"w")
                print("Starting %s" % logfile)
                p = subprocess.Popen(arglist, stdout=outputlog, stderr=outputerr)
                time.sleep(5)
                processes.append(p)
                try:
                     status=p.poll()
                except:
                     write_log("%s : Replica %s sub-block failure. Exiting" % logfile )
                     #return False
##debug
##debug        for p in processes:
##debug                try:
##debug                     status=p.poll()
##debug                except:
##debug                     write_log("%s : Replica %s sub-block failure. Exiting" % logfile )
##debug                     #return False

        print("Waiting WF ")
        for p in processes:
                p.wait()

        bgqtools.free_blocks(blocks)

##debug        time.sleep(4000)
        print("Finish WF ")
        return


if __name__ == "__main__":
        main()
# qmwf : quantum mechanics workflow for data science
# author: alvarovm at gihub

