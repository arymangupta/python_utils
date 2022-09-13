import os
import json
import time
import logging
import datetime
import traceback
import threading
from pathlib import Path

from vsp_defines import VspKeys

logger = logging.getLogger('')

class VSPStats:
    '''This class maintains all stats'''
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(VSPStats, cls).__new__(cls)
        return cls.__instance
    
    def Setup(self, vcomp_name, enabled, gconfigs):
        self._stop = threading.Event()
        self._vcomp_name = vcomp_name
        self._enabled = False
        stats_root = gconfigs.get(VspKeys.CFG_STATS_ROOT_DIR, None)
        if not enabled or not stats_root:
            logging.info("{} stats are disabled".format(vcomp_name))
            return 

        self._stats = {}
        self._stats_lock = threading.Lock()
        self._stats_add_lock = threading.Lock()
        self._stat_enum = 0

        self._stats_comp = {}
        self._stats_comp_lock = threading.Lock()
        self._stats_comp_add_lock = threading.Lock()
        self._stat_comp_enum = 0
        

        self.gconfigs = gconfigs
        vcomp_stats_path = gconfigs.get(VspKeys.CFG_STATS_PATH, '{}'.format(vcomp_name.lower()))
        stats_path = os.path.join(stats_root, vcomp_stats_path)

        if not os.path.exists(stats_root):
            logging.warning("VSP stats root path {} does not exist; not logging stats".format(stats_root))
            return

        if not os.path.exists(stats_path):
            try:
                Path(stats_path).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logging.error("Failed to create {}; Exiting".format(stats_path))
                logging.debug("Exception info: {}".format(e))
                self._enabled = False
                return
        
        stats_path = os.path.join(stats_root, vcomp_stats_path, '{}.stats'.format(vcomp_stats_path))

        logging.info("{} stats written to {} every {} milliseconds".format(vcomp_name, stats_path, gconfigs.get(VspKeys.CFG_STATS_REFRESH_RATE)))
        self._enabled = True

        #Start VSP stats thread
        self._cthread = threading.Thread(target=self._stats_thread)
        self._cthread.start()

    def _get_new_enum(self):
        with self._stats_add_lock:
            e = self._stat_enum
            self._stat_enum += 1
        return e
    
    def _get_new_comp_enum(self):
        with self._stats_comp_add_lock:
            e = self._stat_comp_enum
            self._stat_comp_enum += 1
        return e

    def register_stat(self, class_name, stat_desc, protected=False):
        if not self._enabled:
            return 0
        e = self._get_new_enum()
        with self._stats_lock:
            self._stats[e] = {
                'count':0,
                'class':class_name,
                'desc':stat_desc,
                'protected':protected
            }
        return e

    def register_comp_stat(self, comp, stat_desc, protected=False):
        if not self._enabled:
            return 0
        e = self._get_new_comp_enum()
        with self._stats_comp_lock:
            if comp not in self._stats_comp:
                self._stats_comp[comp] = {}
            self._stats_comp[comp][e] = {
                'count':0,
                'desc':stat_desc,
                'protected':protected
            }
        return e

    def stop(self):
        self._stop.set()

    def reset_stats(self):
        if not self._enabled:
            return
        with self._stats_lock:
            for k,v in self._stats.items():
                if not v['protected']:
                    v['count'] = 0
        with self._stats_comp_lock:
            for k,v in self._stats_comp.items():
                for k1,v1 in v.items():
                    if not v1['protected']:
                        v1['count'] = 0

    def get_stat(self, stat_enum):
        if not self._enabled:
            return 0
        rval = 0
        with self._stats_lock:
            if stat_enum in self._stats:
                rval = self._stats[stat_enum]['count']
        return rval
    
    def update_stat(self, stat_enum, val):
        if not self._enabled:
            return 
        with self._stats_lock:
            if stat_enum in self._stats:
                self._stats[stat_enum]['count'] = val

    def inc_stat(self, stat_enum):
        if not self._enabled:
            return
        with self._stats_lock:
            if stat_enum in self._stats:
                self._stats[stat_enum]['count'] += 1
    
    def dec_stat(self, stat_enum):
        if not self._enabled:
            return
        with self._stats_lock:
            if stat_enum in self._stats:
                self._stats[stat_enum]['count'] -= 1

    def reset_comp_stats(self, comp):
        if not self._enabled:
            return
        with self._stats_comp_lock:
            for k,v in self._stats_comp.get(comp,{}).items():
                if not v['protected']:
                    v['count'] = 0
 
    def get_comp_stat(self, comp, stat_enum):
        if not self._enabled:
            return 0 
        rval = 0
        with self._stats_comp_lock:
            if stat_enum in self._stats_comp[comp]:
                rval = self._stats_comp[comp][stat_enum]['count']
        return rval
    
    def update_comp_stat(self, comp, stat_enum, val):
        if not self._enabled:
            return
        with self._stats_comp_lock:
            if comp in self._stats_comp:
                if stat_enum in self._stats_comp[comp]:
                    self._stats_comp[comp][stat_enum]['count'] = val

    def inc_comp_stat(self, comp, stat_enum):
        if not self._enabled:
            return
        with self._stats_comp_lock:
            if comp in self._stats_comp:
                if stat_enum in self._stats_comp[comp]:
                    self._stats_comp[comp][stat_enum]['count'] += 1
    
    def dec_comp_stat(self, comp, stat_enum):
        if not self._enabled:
            return
        with self._stats_comp_lock:
            if comp in self._stats_comp:
                if stat_enum in self._stats_comp[comp]:
                    self._stats_comp[comp][stat_enum]['count'] -= 1
    
    def _update_stats_file(self):
        ts = datetime.datetime.now().isoformat(sep=' ')
        stats_root = self.gconfigs.get(VspKeys.CFG_STATS_ROOT_DIR)
        vcomp_stats_path = self.gconfigs.get(VspKeys.CFG_STATS_PATH)
        stats_path = os.path.join(stats_root, vcomp_stats_path)
        if not os.path.exists(stats_path):
            Path(stats_path).mkdir(parents=True, exist_ok=True)
        
        stats_path = os.path.join(stats_root, vcomp_stats_path, '{}.stats'.format(vcomp_stats_path))

        with open(stats_path, 'w') as f:
            f.write("{}\n".format(ts)) 
            f.write("{} stats\n".format(self._vcomp_name))
            f.write("{:20.20} {:80.80} {}\n".format("Class", "Stats Description", "Count"))
            for k,v in self._stats.items():
                f.write("{:20.20} {:80.80} {}\n".format(v.get('class'), v.get('desc'), v.get('count')))
            f.write("\n")
            if len(self._stats_comp) > 0:
                f.write("VSP service-specific stats\n")
                for k,v in self._stats_comp.items():
                    f.write("\n{:20.20} {:80.80} {}\n".format("VSP Service", "Stats Description", "Count"))
                    f.write("---------------------------------------------------------------\n")
                    for k1, v1 in v.items():
                        f.write("{:20.20} {:80.80} {}\n".format(k, v1.get('desc'), v1.get('count')))
                        
                    

    def _stats_thread(self):
        i = 0
        while not self._stop.is_set():
            refresh_rate = self.gconfigs.get(VspKeys.CFG_STATS_REFRESH_RATE, 10000)/1000
            time.sleep(refresh_rate)
            with self._stats_lock:
                try:
                    self._update_stats_file()
                except Exception as e:
                    if i < 10:
                        logging.debug("Exception occurred while updating {} stats".format(self._vcomp_name))
                        logging.debug("Exception info: {}".format(traceback.format_exc()))
                    else:
                        logging.error("No longer updating stats file as repeated exceptions have occurred")
                        break
                    i += 1
                    
    def SetPath(self, path):
        origPath = self.gconfigs.get(VspKeys.CFG_STATS_PATH, None)
        if origPath == path:
            logging.debug('no change in stats path %s' % origPath)
            return None
        if origPath is not None:
            self.gconfigs[VspKeys.CFG_STATS_PATH] = path
            logging.info('updated stats path from %s to %s' 
                         % (origPath, self.gconfigs[VspKeys.CFG_STATS_PATH]))

    def SetRefrestRate(self, refreshRate: int):
        orgRefRate = self.gconfigs.get(VspKeys.CFG_STATS_REFRESH_RATE, None)
        if orgRefRate == refreshRate or refreshRate is None or refreshRate < 0:
            logging.debug('no change in refresh rate %d' % orgRefRate)
            return None
        if orgRefRate is not None:
            self.gconfigs[VspKeys.CFG_STATS_REFRESH_RATE] = refreshRate
            logging.info('updated stats refrest rate from %d to %d'
                         % (orgRefRate, self.gconfigs[VspKeys.CFG_STATS_REFRESH_RATE]))
