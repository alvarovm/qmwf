from os import listdir, mkdir, getcwd, makedirs, chdir, getpid
from os.path import isfile, join, isdir, basename, normpath, dirname, curdir
from os.path import splitext, getsize
from shutil import move, copyfile
import uuid
import json
import numpy as np
from external_libs.filelock import FileLock

#
# defaults
#

mypid = getpid()
listofinputs = []
mypath = getcwd()
logdir = join(mypath, 'output')
inboxdir = join(mypath, 'inbox')
jsondir = join(mypath, 'json')
templatedir = mypath

def change_path(src_dir):
    mypath = src_dir
    logdir = join(mypath, 'output')
    inboxdir = join(mypath, 'inbox')
    jsondir = join(mypath, 'json')
    templatedir = mypath

class inputf:
    def __init__(self):
        self.fullpath = ''
        self.pname=''
        self.lock ='no'
        self.id =uuid.uuid4()
#   def __del__(self):
#       print 'adios'

#print journalsdir
def total_inputfiles():
    inputfiles=[f for f in listdir(inboxdir) if isfile(join(inboxdir, f))]
    counter = 0
    for j in inputfiles:
        if j.endswith(".json"):
            counter +=1
    #return len(inputfiles)
    return counter

def create_list():
    inputfiles=[f for f in listdir(inboxdir) if isfile(join(inboxdir, f))]
    for j in inputfiles:
        if j.endswith(".json"):
            input_fullpath=join(inboxdir,j)
            pp = inputf()
            pp.fullpath=input_fullpath
            pp.pname=(splitext(j))[0]
            try:
                with open(input_fullpath, 'r') as f:
                    info = json.load(f)
                if 'lock' in info:
                    pp.lock = info['lock']
                listofinputs.append(pp)
            except:
                print ("%s : cannot open file"% pp.pname)
                filename = input_fullpath
                move(filename, filename+'.fail')
                pass

def create_list_xyz():
    inputfiles=[f for f in listdir(inboxdir) if isfile(join(inboxdir, f))]
    count = 0
    for j in inputfiles:
        #if j == 100 : break
        if j.endswith(".xyz"):
            input_fullpath=join(inboxdir,j)
            pp = inputf()
            pp.fullpath=input_fullpath
            pp.pname=(splitext(j))[0]
            listofinputs.append(pp)
            count = count + 1
    return count


def get_coords(xyzfile):
    xyzlines = open(xyzfile, 'r').read()
    return get_xyz(xyzlines)

def get_xyz(arcfile):
    import re
    print arcfile
    coord = re.findall("(\w*)\s+(\-?\d+(?:\.\d+)?)\s*(\-?\d+(?:\.\d+)?)\s*(\-?\d+(?:\.\d+)?)\s*(\d)\s*(\-?\d+(?:\.\d+)?)\s*(\-?\d+(?:\.\d+)?)\s*(\-?\d+(?:\.\d+)?)", arcfile)
    #coord = re.findall("(\w*)\s*(\-?\d+(?:\.\d+)?)\s*(\-?\d+(?:\.\d+)?)\s*(\-?\d+(?:\.\d+)?)", arcfile)
    coords = []
    for i in coord:
        coords.append(dict(element=i[0], x=float(i[1]), y=float(i[2]), z=float(i[3])))
    return coords


def print_geom_in(e):
    outpath = get_outpath(e)
    pnamexyz = get_name_file(e) + '.xyz'
    if isfile(pnamexyz):
        coords = get_coords(pnamexyz)
        geomfile = join(outpath,'geometry.in')
        try:
            with open(geomfile, 'w') as fp:
                for e in coords:
                    fp.write(' atom %.8f %.8f %.8f %s ' %  ( e['x'], e['y'], e['z'], e['element'] ))
                    fp.write('\n' )
            return True
        except:
            print('%s: cannot write geomini' %  get_name_file(e))
            return None
    else:
        print('%s: cannot find xyz' %  get_name_file(e))
        return None


def pick_one_n_move(e):
    pname = get_name(e)
    outpath = join(logdir, pname)
    if not create_dir(outpath):
        print('%s: cannot create dir' % pname)
        return None
    xyzinput = get_fullpath_inputfile(e)
    xyzoutput = join(outpath, pname+ '.xyz')
    print xyzinput
    print xyzoutput
    if not move_file(xyzinput, xyzoutput):
        print('%s: cannot be moved' % pname)
        return False
    return True

def get_bestconf(e, info, jobtype='mopac'):
# returns best conformer from semi-empirical
#   info = load_json(e)
    try :
#       if not jobtype in info["FILTERED"][0]:
#           return None
#       else:
        nconf = len(info["FILTERED"][0][jobtype])
        econf = np.empty([nconf])
        for key, value in enumerate(info["FILTERED"][0][jobtype]):
            econf[key] =  value['properties']['electronic_energy']
        return econf.argsort()[0]
    except:
        return None

def get_lock(e, info):
  #  info  = load_json(e)
    try:
        lock = info['lock']
        print("%s : this is lock = %s" %(mypid,lock))
        return lock
    except :
    #return listofinputs[e].lock
        return 'no'

def put_lock(e, lock, info):
    listofinputs[e].lock = lock
    pname = get_name(e)
    #print info
    print("%s : this is lock = %s" %(pname,lock))
    info['lock'] = lock
    store_json(e, info)

def clean_db_for_job(e, job):
    info = load_json(e)
    if not job in info:
        put_lock(e, 'no', info)

def clean_db_for_job2(e, job):
    info = load_json(e)
    lock = get_lock(e, info)
    pname = get_name(e)
    print ("%s: has a lock = %s" %(pname,lock))

    if lock == 'ready':
        if not job in info["FILTERED"][0]:
            put_lock(e, 'no', info)

def clean_db(e):
    info = load_json(e)
    if get_lock(e, info) != 'ready':
        put_lock(e, 'no', info)

def clean_db_ready(e):
    info = load_json(e)
    put_lock(e, 'no', info)

#def pick_one(e, job):
##    for e in range(len(listofinputs)) :
#    print e
#    info  = load_json(e)
#    if job in info:
#        return -1
#    if get_lock(e) == 'no':
#        put_lock(e, 'yes')
#        return e
#    if get_lock(e) == 'ready' and not job in info:
#        put_lock(e, 'yes')
#        return e
#    return -1
def pick_one(e, job):
#    for e in range(len(listofinputs)) :
    info  = load_json(e)
#    if 'job' in info:
#        return -1
    pname = get_name(e)
    if info == None:
        return -1, {}
    if get_lock(e, info) == 'no':
        print(" %s :procceedd" % pname)
        put_lock(e, 'yes', info)
        return e , info
    if get_lock(e, info) == 'ready' and not job in info["FILTERED"][0]:
        put_lock(e, 'yes', info)
        return e, info
    return -1, info

def create_dir(folder):
    try:
        makedirs(folder)
        logdir_inplace=True
    except OSError as err:
        #print("OS error: {0}".format(err))
        if isdir(folder):
            logdir_inplace=True
        else :
            print(logdir,'does not exist')
            logdir_inplace = False
    return logdir_inplace


def create_input (e, templ, ext, mols):
    #jinja templates
    from jinja2 import Environment, FileSystemLoader, StrictUndefined
    info = load_json(e)
    config_file=templ
    conf_path=join(templatedir,templ)

    with open(conf_path, 'r') as f:
        conf_fd = json.load(f)

    #jobdef_path = join(mypath,jobdef)
    template_env = Environment(loader=FileSystemLoader(mypath),
                                        undefined=StrictUndefined)

    template_files=conf_fd[u'extra_template_filenames']

    for t in template_files:
        batch_template = template_env.get_template(t)
        input_cont= batch_template.render(jobspec=mols)

        pname = get_name_file(e)
        outpath = join(logdir, pname)
        inputname = join(outpath,pname+ext)

        if not isfile(inputname):
            with open(inputname,'w') as fd:
                fd.write(input_cont)
        else :
            print(inputname, "file exist")
    return


def load_json(e):
    #json_file = get_name_file(e) + '.json'
    #filelock = get_name_file(e)
    filelock = get_name_file(e) + '.json'
    #filelock = json_file(e)
    filename = join(inboxdir, filelock)
    if not isfile(filename):
        return None
    with FileLock(filelock, inboxdir, 600):
        if isfile(filename):
            with open(filename, 'r') as f:
                info = json.load(f)
                return info
        else:
            print("%s: error opening %s" %(get_name_file(e), filename))
            return None

def json_file(e):
    return  full_filename(e,'.json')

def store_json(e,info):
    #filename = json_file(e)
    #filelock = get_name_file(e)
    #filelock = get_name_file(e) + '.json'
    #filelock = json_file(e)
    filelock = get_name_file(e) + '.json'
    filename = join(inboxdir, filelock)
    if not isfile(filename):
        return None
    with FileLock(filelock, inboxdir,600):
        with open(filename,'w') as fd:
            json.dump(info ,fd, indent=4)

def json_update(e, new_info):
    json_info = load_json(e)
    json_info.update(new_info)
    store_json(e, json_info)


def full_filename(e, ext='.txt'):
    #outpath = get_outpath(e)
    filename = get_name_file(e)
    #return join(outpath,filename+ext)
    return join(inboxdir,filename+ext)

def get_outpath(e):
    return join(logdir,get_name_file(e))

def get_name_file(e):
    return listofinputs[e].pname

def get_fullpath_inputfile(e):
    return listofinputs[e].fullpath

def get_id(e):
    return listofinputs[e].id

def get_name(e):
    return listofinputs[e].pname
    #return (splitext( listofpapers[e].pname ))[0]

def prepare_outdir(e):
    pname = get_name_file(e)
    outpath = join(logdir, pname)
    if not create_dir(outpath):
        print('%s: cannot create dir' % pname)
        return False
    try:
        chdir(outpath)
        return copy_json_file(e)
    except:
        print('%s: cannot change dir' % pname)
        print('%s: this  dir' % outpath)
        return False

def chdir_outdir(e):
    pname = get_name_file(e)
    outpath = join(logdir, pname)
    try:
        chdir(outpath)
    except:
        print ("cannot change to dir %s" % outpath)


def copy_json_file(e):
    #TODO overwrite assessment
    #orig = get_fullpath_inputfile(e)
    pname = get_name_file(e)
    outpath = join(logdir, pname)
    orig = join(inboxdir, pname+'.json')
    dest = join(outpath, pname+'.json.copy')
    try:
        copyfile(orig, dest)
        print("%s:Saving a copy of json in outdir" % dest)
        return True
    except:
        print("%s: Fail to a copy of json in outdir" % dest)
        return False

def move_file(a,b):
    if isfile(a):
        if not isfile(b):
            try:
                move(a, b)
                return True
            except:
                print("inputs: file %s cannot moved missing" % a)
            return False
        else:
            print("inputsdd: file %s exist" % b)
            return False
    else:
        print("inputs: file %s is missing" % a)
        return False



#def process_paper(e):
#    if not listofpapers[e].isdone and isfile(listofpapers[e].fullpath):
#
#        jourdir =join(logdir,listofpapers[e].journal)
#        voldir =join(jourdir,listofpapers[e].vol)
#
#        if not create_dir(voldir): print('cannot create dir')
#
#        newaddress=join(voldir,listofpapers[e].pname)
#        logfile= log_file(e)
#tmp
#tmp
#tmp
#tmp        activated = False
#tmp
#tmp        if isfile (logfile):
#tmp            activated=True
#tmp            print listofpapers[e].fullpath
#tmp            print 'someone is working on this'
#tmp        else:
#tmp            try:
#tmp                logo =open(logfile,'w')
#tmp                logo.write('active by rank')
#tmp            except IOError as err:
#tmp                print("OS error log: {0}".format(err))
#tmp                # cycle
#tmp
#tmp        if not activated:
#tmp            #
#tmp            #
#tmp            #
#tmp            #
#tmp            #DO SOMETHING USEFUL HERE
#tmp            #DO SOMETHING USEFUL HERE
#tmp            #
#tmp            #
#tmp            #
#tmp            try:
#tmp                move(listofpapers[e].fullpath,newaddress)
#tmp                listofpapers[e].done=True
#tmp            except IOError as err:
#tmp                print("OS error: {0}".format(err))
#tmp
#tmp    else:
#tmp        if not isfile(listofpapers[e].fullpath):
#tmp            print listofpapers[e].fullpath
#tmp                 print 'not done not present'

#create_list()
#update_isdone()
#process_papers()
#



# qmwf : quantum mechanics workflow for data science
# author: alvarovm at gihub

