
# LWF project has not been initialised
class LWFNotInitialisedError(Exception):
  def __init__(self):
    Exception.__init__(self)

# project file has already been defined
class ProjectFileAlreadyExistsError(Exception):
  def __init__(self):
    Exception.__init__(self)

# file has already been imported
class FileAlreadyImportedError(Exception):
  def __init__(self):
    Exception.__init__(self)

# file has already been imported and is stored on another project_file
class ProjectFileDuplicateFileError(Exception):
  def __init__(self):
    Exception.__init__(self)

# attempt to import a file as a project_file, but the mode has already 
# been consumed by another file
class ProjectFileModeAlreadyTakenError(Exception):
  def __init__(self):
    Exception.__init__(self)
