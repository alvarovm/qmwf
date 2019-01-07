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
            launch_parallel_subprocess(config)
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

def launch_parallel_subprocess(config):
    	'''
    	Launches new replicas using subprocessing
    	'''
        replicas = config['replicas']
        python_command = sys.executable

        comm = config['callscript']

        logfile_path = os.path.join(src_dir,'log')
        try:
            os.mkdir(logfile_path)
        except:
            print("%s dir is in place" % logfile_path)

        processes = []
        handler = functools.partial(receive_signal, processes)
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)

        for rep in range(replicas):
            print 'jola'
            arglist = [python_command, comm]

            logfile = os.path.join(logfile_path,"nwchem_log_"+str(rep)+"_"+str(os.getpid()))
            errfile = os.path.join(logfile_path,"nwchem_err_"+str(rep)+"_"+str(os.getpid()))
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

        print("Waiting WF ")
        for p in processes:
            p.wait()

        print("Finish WF ")
        return

##thetadef launch_parallel_theta():
##theta    import multiprocessing
##theta    import socket, sys
##theta    sys.path.append("/home/richp/rpm/BUILD/cobalt-1.0.1/build/lib")
##theta    from Cobalt.Util import expand_num_list
##theta
##theta
##theta    print multiprocesssing.cpu_count()
##theta    nodelist = " ".join([str(i) for i in sorted(set(expand_num_list(",".join(sys.argv[1:]))))])
##theta    #global nodelist
##theta
##theta    sname = "parallel_settings"
##theta    output.time_log("aprun parallelization method is called")
##theta
##theta    all_processes = get_all_processes("aprun")
##theta    all_nodes = list(nodelist)
##theta
##theta    output.time_log("All nodes: "+", ".join(map(str,all_nodes)))
##theta    nop = len(all_processes) #Number of processes
##theta    non = len(all_nodes) #Number of nodes
##theta    ppn = int(nop/non) #Processes per node
##theta    npr = [] #Nodes per replica
##theta    ppr = [] #Processes per replica
##theta    nor = 0 #Number of replicas
##theta
##theta    if ui.has_option(sname,"processes_per_replica"):
##theta        ppr = ui.get_eval(sname,"processes_per_replica")
##theta        if ppr >= ppn:
##theta            npr = int(math.ceil(ppr/(ppn+0.0)))
##theta            if ui.has_option(sname,"number_of_replicas"):
##theta                nor = ui.get_eval(sname,"number_of_replicas")
##theta            else:
##theta                nor = non/npr
##theta            npr = [npr]*nor
##theta            ppr = [ppr]*nor
##theta        else:
##theta            rpn = ppn/ppr
##theta            if ui.has_option(sname,"number_of_replicas"):
##theta                nor = ui.get_eval(sname,"number_of_replicas")
##theta            else:
##theta                nor = non*rpn
##theta            npr = [int(0+(x%3)==0) for x in range(1,nor+1)]
##theta            ppr = [ppr]*nor
##theta    else:
##theta        message = "aprun parallelization method requires the setting "
##theta        message += "setting the following parameter within parallel_settings: "
##theta        message += "nodes_per_replica, processes_per_replica"
##theta        raise KeyError(message)
##theta
##theta
##theta    # Setup individual ui.conf for each replica
##theta    processes = []
##theta    new_ui = deepcopy(ui)
##theta    new_ui.set(sname,"parallelization_method","serial")
##theta    if not ui.has_option(sname,"processes_per_node"):
##theta        new_ui.set(sname,"processes_per_node",str(ppn))
##theta    python_command = ui.get(sname,"python_command")
##theta    new_ui.set(sname,"im_not_master_process","TRUE")
##theta
##theta    # Main loop to launch parallel replicas
##theta    node_count = 0
##theta
##theta    for i in range(nor):
##theta        if node_count == non:
##theta            node_count = 0
##theta        new_ui.set(sname,"replica_name",misc.get_random_index())
##theta        new_ui.set(sname,"processes_per_replica",str(ppr[i]))
##theta        new_ui.set(sname,"allocated_nodes","['"+str(all_nodes[node_count])+"']")
##theta        conf_path = os.path.join(fh.conf_tmp_dir,new_ui.get(sname,"replica_name")+".conf")
##theta        exe_path = os.path.join(fh.conf_tmp_dir,new_ui.get(sname,"replica_name")+".exe")
##theta        f = open(conf_path,"w")
##theta        new_ui.write(f)
##theta        f.close()
##theta
##theta        p = subprocess.Popen(["aprun","-n","1","-L",all_nodes[1],python_command,fh.GAtor_master_path,conf_path])
##theta        processes.append(p)
##theta
##theta        #arglist = [python_command,fh.GAtor_master_path,conf_path]
##theta        output.time_log("Running: "+" ".join(map(str,arglist)))
##theta        #p = subprocess.Popen(arglist)
##theta        #processes.append(p)
##theta        #node_count +=1
##theta    for p in processes:
##theta        p.wait()

if __name__ == "__main__":
        main()
# qmwf : quantum mechanics workflow for data science
# author: alvarovm at gihub

