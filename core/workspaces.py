# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 21:47:05 2017

@author: a002087
"""

import os
import shutil
import sys
import datetime
import codecs

current_path = os.path.dirname(os.path.realpath(__file__))[:-4]
sys.path.append(current_path)

import core


###############################################################################
class WorkStep(object):
    """
    A WorkStep holds information about the file structure and 
    contains all methodes operating on a specific workstep. 
    """
    def __init__(self, name=None, parent_directory=None):
        if not all([name, parent_directory]): 
            return 
        self.name = name 
        self.parent_directory = parent_directory 
        self.step_directory = '/'.join([self.parent_directory, self.name]) 
        print('Initiating WorkStep: {}'.format(self.step_directory))
        
        self._load_attributes()
        
        self._set_directories()
        
        self._create_folder_structure()
        self.load_all_files()
        self._check_folder_structure()        
        
    #==========================================================================
    def _create_folder_structure(self):
        """
        Sets up the needed folder structure for the workstep. 
        Folders ar added if they dont exist. 
        """
        if not os.path.exists(self.step_directory): 
            os.makedirs(self.step_directory)
            
        for path in self.directory_paths.values():
            if not os.path.exists(path):
                os.makedirs(path)
        
    #==========================================================================
    def _create_file_paths(self): 
                
        # Indicator settings 
        self.indicator_settings_paths = {}
        for file_name in os.listdir(self.directory_paths['indicator_settings']): 
            if file_name.endswith('.set'):
                file_path = '/'.join([self.directory_paths['indicator_settings'], file_name])
                indicator = file_name.split('.')[0]
                self.indicator_settings_paths[indicator] = file_path
        
    #==========================================================================
    def _check_folder_structure(self):
        #TODO: make check of workspace folder structure
        all_ok = True
        for key, item in self.directory_paths.items():
            if os.path.isdir(item):
                continue
            else:
                all_ok = False
                try:
                    # MW: Does not work for me in Spyder
                    raise('PathError')
                except:
                    pass
                print('no folder set for: {}'.format(item))
                
        return all_ok
        
    #==========================================================================
    def _load_attributes(self): 
        # Load attributes to be able to check what has been done
        self.data_filter = None
        self.indicator_settings = {}
        
    #==========================================================================
    def _save_ok(self):
        if self.name == 'default':
            print('Not allowed to save default workspace!')
            return False
        return True
    
    #==========================================================================
    def _set_directories(self):
        self.directory_paths = {}
        #set paths
        self.directory_paths['data_filters'] = self.step_directory + '/data_filters'
        self.directory_paths['settings'] = self.step_directory + '/settings'
        self.directory_paths['indicator_settings'] = self.step_directory + '/settings/indicator_settings'
        self.directory_paths['output'] = self.step_directory + '/output'
        self.directory_paths['results'] = self.step_directory + '/output/results'
    
    #==========================================================================
    def add_files_from_workstep(self, step_object=None, overwrite=False):
        """
        Copy files from given workstep. Option to overwrite or not. 
        This method shold generaly be used when copying step_0 or a whole subset. 
        DONT USE FOR COPYING SINGLE STEPS NUMBERED 1 and up. 
        """ 
        for from_file_path in step_object.get_all_file_paths_in_workstep():
            to_file_path = from_file_path.replace(step_object.step_directory, self.step_directory) 
            if os.path.exists(to_file_path) and not overwrite:
                continue
            to_directory = os.path.dirname(to_file_path)
            if not os.path.exists(to_directory):
                # If directory has been added in later versions of the ekostat calculator
                os.makedirs(to_directory) 
            # Copy file
            shutil.copy(from_file_path, to_file_path)
        
        self.load_all_files()    
            
        
    #==========================================================================
    def get_all_file_paths_in_workstep(self): 
        """
        Returns a sorted list of all file paths in the workstep tree. 
        Generally this method is used when copying the workstep. 
        """
        file_list = []
        for root, dirs, files in os.walk(self.step_directory): 
                for f in files:
                    file_list.append('/'.join([root, f]).replace('\\', '/'))
        return sorted(file_list)
    
    #==========================================================================
    def get_data_filter_object(self):
        return self.data_filter
    
    #==========================================================================
    def get_data_filter_info(self): 
        """
        Returns a dict with data filter names as keys. 
        Every key contains a list of the active filters. 
        """
        self.first_filter.get_filter_info()
        
    #==========================================================================
    def get_indicator_filter_settings(self, indicator): 
        """
        Returns the filter settings for the given indicator. 
        """
        return self.indicator_filter_settings.get(indicator, False)
    
    #==========================================================================
    def get_indicator_tolerance_settings(self, indicator): 
        """
        Returns the tolerance settings for the given indicator. 
        """
        return self.indicator_tolerance_settings.get(indicator, False)
    
    #==========================================================================
    def get_indicator_ref_settings(self, indicator): 
        """
        Returns the reference settings for the given indicator. 
        """
        return self.indicator_ref_settings.get(indicator, False)
    
    #==========================================================================
    def get_indicator_settings_name_list(self):
        return sorted(self.indicator_settings.keys()) 
    
    #==========================================================================
    def load_all_files(self): 
        self._create_file_paths()
        self.load_data_filter()
        self.load_indicator_filters()
        
    #==========================================================================
    def load_data_filter(self):
        # Load all settings file in the current WorkSpace filter folder... 
        self.data_filter = core.DataFilter(self.directory_paths['data_filters']) 
        
        

    #==========================================================================
    def load_indicator_filters(self): 
        """
        Loads all types of settings, data and config files/objects. 
        """
        
        # All indicators in directory should be loaded automatically         
        # Load indicator setting files. Internal attr (_) since they are only used by other objects.  
        self._indicator_setting_files = {} 
        for indicator, file_path in self.indicator_settings_paths.items(): 
            self._indicator_setting_files[indicator] = core.SettingsFile(file_path)
            if self._indicator_setting_files[indicator].indicator != indicator:
                print('Missmatch in indicator name and object name! {}:{}'.format(self._indicator_setting_files[indicator].indicator, indicator))
            
        # Load Filter settings. Filter settings are using indicator_setting_files-obects as data
        self.indicator_filter_settings = {} 
        for indicator, obj in self._indicator_setting_files.items():
            self.indicator_filter_settings[indicator] = core.SettingsFilter(obj)
            
        # Load Ref settings. Filter settings are using indicator_setting_files-obects as data
        self.indicator_ref_settings = {} 
        for indicator, obj in self._indicator_setting_files.items():
            self.indicator_ref_settings[indicator] = core.SettingsRef(obj) 
            
        # Load Tolerance settings. Filter settings are using indicator_setting_files-obects as data
        self.indicator_tolerance_settings = {} 
        for indicator, obj in self._indicator_setting_files.items():
            self.indicator_tolerance_settings[indicator] = core.SettingsTolerance(obj)
            
    #==========================================================================
    def update_data_filter_settings(self, filter_settings=None):
        """
        filter_settings are dicts like: 
            filter_settings[type_area][variable] = value 
        """
        if filter_settings: 
            filter_settings.set_values(filter_settings)
            
    #==========================================================================
    def update_indicator_filter_settings(self, indicator=None, filter_settings=None):
        """
        filter_settings are dicts like: 
            filter_settings[type_area][variable] = value 
        """
        if filter_settings: 
            filter_object = self.indicator_filter_settings[indicator] 
            filter_object.set_values(filter_settings) 
        
    #==========================================================================
    def save_indicator_settings(self, indicator): 
        if not self._save_ok(): 
            return 
        self.indicator_settings[indicator].save_file() # Overwrites existing file if no file_path is given
        return True 
    
    #==========================================================================
    def save_all_indicator_settings(self): 
        if not self._save_ok(): 
            return 
        all_ok = True
        for obj in self.indicator_settings.values():
            if not obj.save_file() :
                all_ok = False
        return all_ok
        
    #==========================================================================
    def set_data_filter(self, filter_type='', filter_name='', data=None, save_filter=True): 
        """
        Sets the data_filter. See data_filter.set_filter for more information. 
        """ 
        data_filter = self.get_data_filter_object() 
        data_filter.set_filter(filter_type=filter_type, 
                               filter_name=filter_name, 
                               data=data, 
                               save_filter=save_filter)    
            
    #==========================================================================
    def show_settings(self):
        print('first_filter:')
        self.first_filter.show_filter()
        
        
###############################################################################
class Subset(object):
    """
    Class to hold subset paths and objects. 
    """
    def __init__(self, name=None, parent_directory=None, alias=False, max_step_nr=2): 
        assert all([name, parent_directory])
        self.name = name 
        self.parent_directory = parent_directory.replace('\\', '/')
        self.subset_directory = '/'.join([self.parent_directory, self.name]) 
        self.max_step_nr = max_step_nr
        print('-'*100)
        print('Initiating Subset: {}'.format(self.subset_directory))
        
        self._load_attributes()
        self._load_steps() 
        
        self._load_config()
        
        if alias not in [False, None]: 
            self.set_alias(alias)
        
    #==========================================================================
    def _load_attributes(self): 
        self.steps = {}
        
    #==========================================================================
    def _load_config(self): 
        self.config_file_path = self.subset_directory + '/subset.cfg'
        self.config = self.Config(self.config_file_path)
        
        
    #==========================================================================
    def _load_steps(self): 
        if not os.path.exists(self.subset_directory): 
            os.makedirs(self.subset_directory)
        step_list = [item for item in os.listdir(self.subset_directory) if '.' not in item]
        print('step_list', step_list)
        for step in step_list:
            self.add_workstep(step)
        
    #==========================================================================
    def add_files_from_subset(self, subset_object=None, overwrite=False):
        """
        Copy files from given subset. Option to overwrite or not. 
        This method is used to copy (branching) an entire subset. 
        """ 
        for step in subset_object.get_step_list(): 
            print('step:', step)
            self.add_workstep(step)
            step_object = subset_object.get_step_object(step)
            self.steps[step].add_files_from_workstep(step_object=step_object, 
                                                     overwrite=overwrite)
            
        # Copy config file
        if os.path.exists(subset_object.config_file_path):
            if os.path.exists(self.config_file_path) and not overwrite: 
                return False 
            
            shutil.copy(subset_object.config_file_path, self.config_file_path)
            self._load_config()
        return True
            
            
    #==========================================================================
    def add_workstep(self, step=None):
        if not step:
            step_list = self.get_step_list()
            for s in range(1, self.max_step_nr+1): 
                st = 'step_{}'.format(s)
                if st not in step_list:
                    step = st
                    break
            if not step:
                print('Cannot add another step!')
                return
        
        self.steps[step] = WorkStep(name=step, parent_directory=self.subset_directory)

        
    #==========================================================================
    def delete_workstep(self, step=None): 
        """
        step is like 'step_1', 'step_2' and so on. 
        """
        if step in self.subset_dict.keys(): 
            # TODO: Delete files and directories. How to make this safe? 
            self.steps.pop(step)
    
    #==========================================================================
    def get_alias(self): 
        alias = self.config.get_config('alias') 
        if not alias:
            return '' 
        
    #==========================================================================
    def get_all_file_paths_in_subset(self): 
        """
        Returns a sorted list of all file paths in the subset tree. 
        """
        file_list = []
        for root, dirs, files in os.walk(self.subset_directory): 
                for f in files:
                    file_list.append('/'.join([root, f]).replace('\\', '/'))
        return sorted(file_list)

    #==========================================================================
    def get_data_filter_info(self, step): 
        """
        Returns a dict with information about the active filters. 
        """
        data_filter = self.get_data_filter_object(step)
        if not data_filter:
            return False
        return data_filter.get_data_filter_info()
    
    #==========================================================================
    def get_data_filter_object(self, step): 
        """
        Returns the data filter for the given step. 
        """
        step = get_step_name(step)
        if step not in self.get_step_list():
            return False 
        return self.steps[step].data_filter 
    
    #==========================================================================
    def get_step_list(self): 
        return sorted(self.steps.keys())
    
    #==========================================================================
    def get_step_object(self, step): 
        step = get_step_name(step)
        return self.steps.get(step, False)
        
    #==========================================================================
    def get_step_1_object(self): 
        return self.get_step_object('step_1')
    
    #==========================================================================
    def get_step_2_object(self): 
        return self.get_step_object('step_2')
    
    #==========================================================================
    def load_data(self, step): 
        if step not in self.steps.keys():
            print('Invalid step "{}" given to load data in subset "{}"!'.format(step, self.name))
            return False 
            
        self.steps[step].load_data()
    
    #==========================================================================
    def set_alias(self, alias):
        print('New alias for subset "{}" => "{}"'.format(self.config.get_config('alias'), alias))
        self.config.set_config('alias', alias)
        
    #==========================================================================
    def set_data_filter(self, step='', filter_type='', filter_name='', data=None, save_filter=True):  
        step_object = self.get_step_object(step)
        if not step_object:
            return False 
        return step_object.set_data_filter(filter_type=filter_type, filter_name=filter_name, data=data, save_filter=save_filter)
    
    
    #==========================================================================
    #==========================================================================
    class Config(dict): 
        def __init__(self, file_path): 
            self.file_path = file_path
            if not os.path.exists(file_path):
                with codecs.open(file_path, 'w', encoding='cp1252') as fid: 
                    fid.write('\n')
            else:
                with codecs.open(file_path, encoding='cp1252') as fid:
                    for line in fid: 
                        line = line.strip()
                        if not line:
                            continue
                        split_line = [item.strip() for item in line.split(';')]
                        item, value = split_line
                        self[item] = value
                    
        def get_config(self, item):
            return self.get(item)
        
        def set_config(self, item, value):
            self[item] = value
            self.save_file()
            
        def save_file(self):
            with codecs.open(self.file_path, 'w', encoding='cp1252') as fid:
                for item, value in sorted(self.items()):
                    line = ';'.join([item, value])
                    fid.write('{}\n'.format(line))
            

###############################################################################
class WorkSpace(object):
    """
    Class to load workspace
    Holds step_0 and subsets. 
    """
    def __init__(self, 
                 name=None, 
                 parent_directory=None, 
                 resource_directory=None, 
                 nr_subsets_allowed=4): 
        
        assert all([name, parent_directory])
        assert nr_subsets_allowed
        
        self.name = name 
        self.parent_directory = parent_directory.replace('\\', '/')
        self.resource_directory = resource_directory.replace('\\', '/')
        self.workspace_directory = '/'.join([self.parent_directory, self.name])
        self.nr_subsets_allowed = nr_subsets_allowed
        
        print('')
        print('='*100)
        print('Initiating WorkSpace: {}'.format(self.workspace_directory)) 
        
        self._load_attributes()
        
#        print('Parent directory is: {}'.format(self.parent_directory))
        
        self._setup_workspace()
            
    #==========================================================================
    def _load_attributes(self): 
        # Setup default paths 
        self.directory_path_subsets = {}
        self.directory_path_input_data = self.workspace_directory + '/input_data'
        self.directory_path_subset = self.workspace_directory + '/subsets'
        
        # Load attributes to be able to check what has been done
        self.step_0 = None 
        
        # Subset (convert to char)
        self.subset_list = [chr(x+65) for x in range(self.nr_subsets_allowed)]
        self.subset_dict = {}
        
    #==========================================================================
    def _save_ok(self):
        if self.name == 'default':
            print('Not allowed to save default workspace!')
            return False
        return True
        
    #==========================================================================
    def _setup_workspace(self):
        """
        Adds paths and objects for the workspace. 
        """        
        # Create input data folder if non existing
        if not os.path.exists(self.directory_path_input_data):
            os.makedirs(self.directory_path_input_data)
        
        # Initiate one subset as default 
        if not os.path.exists(self.directory_path_subset):
            os.makedirs(self.directory_path_subset)
            
        subsets = os.listdir(self.directory_path_subset)
#        print('subsets', subsets)
        if subsets:
            for s in subsets:
                self.add_subset(s)
        else:
            self.add_subset()
            
        # Step 0
#        if not os.path.exists(self.directory_path_step_0):
#            os.makedirs(self.directory_path_step_0)
        self.step_0 = WorkStep(name='step_0', 
                               parent_directory=self.workspace_directory)
        
        # Set data and index handler
        self.data_handler = core.DataHandler(input_data_directory=self.directory_path_input_data, 
                                             resource_directory=self.resource_directory)
        
        self.index_handler = core.IndexHandler(workspace_object=self, 
                                               data_handler_object=self.data_handler)
        
    #==========================================================================
    def add_files_from_workspace(self, workspace_object=None, overwrite=False):
        """
        Copy files from given workspace. Option to overwrite or not. 
        This method is used to copy an entire workspace. 
        """ 
        # Step 0
        if workspace_object.step_0: 
            self.step_0 = WorkStep(name='step_0', 
                          parent_directory=self.workspace_directory) 
            self.step_0.add_files_from_workstep(step_object=workspace_object.step_0, 
                                                overwrite=overwrite)
                
        # Subsets
        for subset in workspace_object.get_subset_list():
            self.add_subset(subset)
            self.subset_dict[subset].add_files_from_subset(subset_object=workspace_object.subset_dict[subset], 
                                                           overwrite=overwrite)
            
        # Data         
        for from_file_path in workspace_object.get_all_file_paths_in_input_data():
            to_file_path = from_file_path.replace(workspace_object.workspace_directory, self.workspace_directory)
            if os.path.exists(to_file_path) and not overwrite:
                continue
            to_directory = os.path.dirname(to_file_path)
            if not os.path.exists(to_directory):
                # If directory has been added in later versions of the ekostat calculator
                os.makedirs(to_directory)
            # Copy file
            shutil.copy(from_file_path, to_file_path)
        
    #==========================================================================
    def add_subset(self, sub=None, alias=False): 
#        print(sub)
#        print(self.subset_list)
        if not sub:
            for s in self.subset_list:
                if s not in self.subset_dict.keys():
                    sub = s
                    break
            if not sub:
                print('Cannot add another subset. Maximum subset limit has been reached!')
                return False
        elif sub in self.subset_dict.keys():
            print('Given subset is already present!')
            return False
        elif sub not in self.subset_list:
            print('Invalid subset name: {}'.format(sub))
            return False
        
#        print('== {}'.format(sub))
        self.directory_path_subsets[sub] = self.directory_path_subset + '/{}'.format(sub)
        self.subset_dict[sub] = Subset(name=sub, 
                                       parent_directory=self.directory_path_subset, 
                                       alias=alias)
        return sub 
    
    #==========================================================================
    def apply_first_filter(self): 
        """
        Applies the first filter to the index_handler. 
        """
        all_ok = self.index_handler.add_filter(filter_object=self.step_0.data_filter, filter_level=0)
        return all_ok
        
    #==========================================================================
    def apply_subset_filter(self, subset):
        """
        Applies the data filter for the given subset. 
        This is not fully handled by the index_handler. 
        """
        if subset not in self.get_subset_list():
            return False
        sub_object = self.get_step_1_object(subset)
        all_ok = self.index_handler.add_filter(filter_object=sub_object.data_filter, filter_level=1, subset=subset)
        return all_ok
        
    #==========================================================================
    def copy_subset(self, sourse_subset_name=None, target_subset_name=None, new_alias=False): 
        assert all([sourse_subset_name, target_subset_name])
        if not self.add_subset(sub=target_subset_name, alias=new_alias):
            return False
        return self.subset_dict[target_subset_name].add_files_from_subset(self.subset_dict[sourse_subset_name], overwrite=True)
    
    #==========================================================================
    def delete_subset(self, subset_name=None): 
        """
        subset_name is like 'A', 'B' and so on. Consider to use alias as option. 
        """
        if subset_name in self.subset_dict.keys(): 
            # TODO: Delete files and directories. How to make this safe? 
            self.subset_dict.pop(subset_name)
            self.directory_path_subsets.pop(subset_name)
            return True
        return False
            
    #==========================================================================
    def get_all_file_paths_in_workspace(self): 
        """
        Returns a sorted list of all file paths in the workspace tree. 
        """
        file_list = []
        for root, dirs, files in os.walk(self.workspace_directory): 
                for f in files:
                    file_list.append('/'.join([root, f]).replace('\\', '/'))
        return sorted(file_list)
    
    #==========================================================================
    def get_all_file_paths_in_input_data(self):
        file_list = []
        for root, dirs, files in os.walk(self.directory_path_input_data): 
                for f in files:
                    file_list.append('/'.join([root, f]).replace('\\', '/'))
        return sorted(file_list)
    
    #==========================================================================
    def get_data_filter_object(self, step=None, subset=None): 
        step_object = self.get_step_object(step=step, subset=subset)
        if not step_object:
            return False
        return step_object.get_data_filter_object()
        
    #==========================================================================
    def get_data_filter_info(self, step=None, subset=None): 
        data_filter = self.get_data_filter_object(step=step, subset=subset)
        if not data_filter:
            return False
        return data_filter.get_filter_info()
    
    #==========================================================================
    def get_filtered_data(self, level=None, subset=None): 
        """
        Returns filtered data using the given filter level. 
        """
        if level == None:
            return False
        return self.index_handler.get_filtered_data(level=level, subset=subset)
    
    #==========================================================================
    def get_indicator_settings_name_list(self):
        return sorted(self.indicator_settings.keys())
    
    #==========================================================================
    def get_subset_list(self):
        return sorted(self.subset_dict.keys())
    
    #==========================================================================
    def get_subset_object(self, subset): 
        return self.subset_dict.get(subset, False)
    
    #==========================================================================
    def get_step_object(self, step=None, subset=None): 
        step = get_step_name(step)
        if step == 'step_0':
            return self.get_step_0_object()
        
        assert all([subset, step])
        
        sub = self.get_subset_object(subset)
        if not sub:
            return False
        return sub.get_step_object(step)
    
    #==========================================================================
    def get_step_0_object(self): 
        return self.step_0 
    
    #==========================================================================
    def get_step_1_object(self, subset): 
        return self.subset_dict[subset].get_step_1_object()
    
    #==========================================================================
    def get_step_2_object(self, subset): 
        return self.subset_dict[subset].get_step_2_object()
    
    #==========================================================================
    def initiate_quality_factors(self, ):
        self.quality_factor_NP = core.QualityFactorNP()
        
    #==========================================================================
    def load_all_data(self): 
        """ 
        Loads all data from the input_data-directory belonging to the workspace. 
        """
        # TODO: Make this part dynamic 
        raw_data_file_path = self.directory_path_input_data + '/raw_data/'
        output_directory = self.directory_path_input_data + '/exports/' 
        """
        # The input_data directory is given to DataHandler during initation. 
        # If no directory is given use the default directory! 
        # This has to be done in physical_chemical, zoobenthos etc. 
        """
        # Row data
        fid_zooben = u'zoobenthos_2016_row_format_2.txt'
        fid_phyche = u'BOS_HAL_2015-2016_row_format_2.txt'
        fid_phyche_col = u'BOS_BAS_2016-2017_column_format.txt' 
        
        self.data_handler.physical_chemical.load_source(file_path=raw_data_file_path + fid_phyche,
                                                        raw_data_copy=True)
        self.data_handler.physical_chemical.load_source(file_path=raw_data_file_path + fid_phyche_col,
                                                        raw_data_copy=True)
        self.data_handler.physical_chemical.save_data_as_txt(directory=output_directory, prefix=u'Column_format')
        
        #raw_data.physical_chemical.raw_data_format
        #raw_data.physical_chemical.row_data.keys()
        #raw_data.physical_chemical.filter_parameters.use_parameters
        
        self.data_handler.zoobenthos.load_source(file_path=raw_data_file_path + fid_zooben,
                                                 raw_data_copy=True)
        self.data_handler.zoobenthos.save_data_as_txt(directory=output_directory, prefix=u'Column_format')
        
        self.data_handler.merge_all_data(save_to_txt=True)
        
    #==========================================================================
    def save_indicator_settings(self, indicator): 
        if not self._save_ok(): 
            return 
        self.indicator_settings[indicator].save_file() # Overwrites existing file if no file_path is given
        return True 
    
    #==========================================================================
    def save_all_indicator_settings(self): 
        if not self._save_ok(): 
            return 
        all_ok = True
        for obj in self.indicator_settings.values():
            if not obj.save_file():
                all_ok = False
        return all_ok 
    
    #==========================================================================
    def set_data_filter(self, step='', subset='', filter_type='', filter_name='', data=None, save_filter=True): 
        step_object = self.get_step_object(step=step, subset=subset)
        if not step_object:
            return False
        print('sdfs')
        return step_object.set_data_filter(filter_type=filter_type, 
                                            filter_name=filter_name, 
                                            data=data, 
                                            save_filter=save_filter)
        
    #==========================================================================
    def set_indicator_settings_filter(self, step='', subset='', filter_type='', filter_name='', data=None, save_filter=True): 
        """
        Use to change indicator settings filter. 
        """
        step_object = self.get_step_object(step=step, subset=subset)
        if not step_object:
            return False
        return step_object.set_data_filter(filter_type=filter_type, 
                                            filter_name=filter_name, 
                                            data=data, 
                                            save_filter=save_filter)

        
    #==========================================================================
    def update_indicator_filter_settings(self, indicator=None, filter_settings=None):
        """
        filter_settings are dicts like: 
            filter_settings[type_area][variable] = value 
        """
        if filter_settings: 
            filter_object = self.indicator_filter_settings[indicator]
            filter_object.set_values(filter_settings)
    
    
    
"""
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
"""


#==============================================================================
#==============================================================================
def get_step_name(step): 
    step = str(step)
    if not step.startswith('step_'):
        step = 'step_' + step
    return step


#==============================================================================
#==============================================================================
#==============================================================================
if __name__ == '__main__':
    if 0:
        directory = 'D:/Utveckling/g_ekostat_calculator/ekostat_calculator_lena/workspaces/default'
        new_directory = 'D:/Utveckling/g_ekostat_calculator/ekostat_calculator_lena/workspaces/active_workspace'
        file_list = []
        new_file_list = []
        for root, dirs, files in os.walk(directory): 
    #            print(root.replace('\\', '/'))
    #             level = root.replace(directory, '').count(os.sep)
    #             indent = ' ' * 4 * (level)
    #             print('{}{}/'.format(indent, os.path.basename(root)))
    #             subindent = ' ' * 4 * (level + 1)
                for f in files:
    #                 file_list.append('/'.join([os.path.basename(root), f]))
                    file_path = '/'.join([root, f]).replace('\\', '/')
                    file_list.append(file_path)
                    new_file_path = file_path.replace(directory, new_directory)
                    new_file_list.append(new_file_path)
                    
    if 1:
        workspace_path = 'D:/Utveckling/g_ekostat_calculator/ekostat_calculator_lena/workspaces'
        w = WorkSpace(name='default', parent_directory=workspace_path)
                    
                    
                    
                    
                    
                    
                    
                    
                