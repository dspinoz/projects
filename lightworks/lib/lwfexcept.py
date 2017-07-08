
# LWF project has not been initialised
class LWFNotInitialisedError(Exception):
  def __init__(self):
    Exception.__init__(self)

# LWF project could not determine config value 
class ConfigValueNotFoundError(Exception):
  def __init__(self,cfg):
    Exception.__init__(self)
    self.cfg = cfg
  def __str__(self):
    return Exception.__str__(self) + self.cfg

# LWF project has not been initialised
class UnsupportedFileModeError(Exception):
  def __init__(self,mode):
    Exception.__init__(self)
    self.mode = mode
  def __str__(self):
    return Exception.__str__(self) + str(self.mode)

# project file has not been added
# project file could not be found
class ProjectFileNotFoundError(Exception):
  def __init__(self,path):
    Exception.__init__(self)
    self.path = path
  def __str__(self):
    return Exception.__str__(self) + self.path
    
# project file has already been defined
class ProjectFileAlreadyExistsError(Exception):
  def __init__(self,path):
    Exception.__init__(self)
    self.path = path
  def __str__(self):
    return Exception.__str__(self) + self.path

# file has not been added
# file could not be found
class FileNotFoundError(Exception):
  def __init__(self):
    Exception.__init__(self)
    
# file has already been imported
class FileAlreadyImportedError(Exception):
  def __init__(self,path):
    Exception.__init__(self)
    self.path = path
  def __str__(self):
    return Exception.__str__(self) + self.path

# file has already been imported and is stored on another project_file
class ProjectFileDuplicateFileError(Exception):
  def __init__(self):
    Exception.__init__(self)

# attempt to import a file as a project_file, but the mode has already 
# been consumed by another file
class ProjectFileModeAlreadyTakenError(Exception):
  def __init__(self):
    Exception.__init__(self)

# scripts/info failed
class FileInfoError(Exception):
  def __init__(self):
    Exception.__init__(self)

# scripts for transcoding failed
class FileFFMPEGError(Exception):
  def __init__(self):
    Exception.__init__(self)
