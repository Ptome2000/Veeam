import os
import time
import datetime
import filecmp
import shutil

def main():
    global originF
    global copyF
    global logF
    originF = input("Provide original folder path: ")
    copyF = input("Provide copy folder path: ")
    logF = input("Provide Log file path: ")
    interval = int(input("Please provide interval in seconds for periodic script execution: "))
    schedule(interval)

def exists():
    #Verify if both folders and log file exist, if not create
    if not os.path.exists(originF):
        os.mkdir(originF)
    if not os.path.exists(copyF):
        os.mkdir(copyF)
    if not os.path.exists(logF):
        open(logF, "x")

def schedule(interval):
    #Basic Interval scheduler with a time.sleep
    while True:
        sync()
        time.sleep(interval)
  
def log_message(operation, folder, logFile):
    #Function to log operation both on terminal and on log file
    print(f"{operation} on {folder}")
    logFile.write(f"{operation} on {folder}\n")

def count_message(operation, number, logFile):
    #Function to see the total of operations made
    print(f"Total of {number} files were {operation}")
    logFile.write(f"Total of {number} files were {operation}\n")

def sync():
    exists()

    #Reset Counters 
    removedCount = 0
    copiedCount = 0
    updatedCount = 0

    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(logF, "a") as logFile:
        logFile.write(f"---Log from {date}---\n")
        print(f"---Log from {date}---")

        copiedCount, updatedCount, removedCount = sync_folder(originF, copyF, logFile, copiedCount, updatedCount, removedCount)

        count_message("copied", copiedCount, logFile)
        count_message("updated", updatedCount, logFile)
        count_message("removed", removedCount, logFile)

        logFile.write("\n")
        print("")

def sync_folder(sourceDir, replicaDir, logFile, copiedCount, updatedCount, removedCount):

    #Compare files in the current folder
    comp = filecmp.dircmp(sourceDir, replicaDir)

    #Copy files or folders from Source folder that don't exist in Replica folder
    for file in comp.left_only:
        sourceFile = os.path.join(sourceDir, file)
        replicaFile = os.path.join(replicaDir, file)
        if os.path.isdir(sourceFile):
            copy_dir(sourceFile, replicaFile, logFile, file)
            copiedCount += len(os.listdir(sourceFile))
        else:
            copy_file(sourceFile, replicaFile, logFile, file)
            copiedCount += 1

    #Remove files or folders from Replica folder that don't exist in Source folder
    for file in comp.right_only:
        replicaFile = os.path.join(replicaDir, file)
        if os.path.isdir(replicaFile):
            removedCount += len(os.listdir(replicaFile))
            remove_dir(replicaFile, logFile, file)    
        else:
            remove_file(replicaFile, logFile, file)
            removedCount += 1

    #Update files from Source folder to Replica folder
    for file in comp.diff_files:
        sourceFile = os.path.join(sourceDir, file)
        replicaFile = os.path.join(replicaDir, file)
        update_file(sourceFile, replicaFile, logFile, file)
        updatedCount += 1

    #Recursively sync common subfolders
    for directory in comp.common_dirs:
        sourceSubDir = os.path.join(sourceDir, directory)
        replicaSubDir = os.path.join(replicaDir, directory)
        copiedCount, updatedCount, removedCount = sync_folder(sourceSubDir, replicaSubDir, logFile, copiedCount, updatedCount, removedCount)

    return copiedCount, updatedCount, removedCount


def copy_file(sourceFile, replicaFile, logFile, filename):
    os.makedirs(os.path.dirname(replicaFile), exist_ok=True)
    shutil.copy2(sourceFile, replicaFile)
    log_message(f"The file {filename} was added successfully", "Replica", logFile)

def copy_dir(sourceFile, replicaFile, logFile, filename):
    shutil.copytree(sourceFile, replicaFile)
    log_message(f"The folder {filename} was added successfully", "Replica", logFile)

def remove_file(replicaFile, logFile, filename):
    os.remove(replicaFile)
    log_message(f"The file {filename} was removed successfully", "Replica", logFile)

def remove_dir(replicaFile, logFile, filename):
    shutil.rmtree(replicaFile)
    log_message(f"The folder {filename} was removed successfully", "Replica", logFile)

def update_file(sourceFile, replicaFile, logFile, filename):
    os.makedirs(os.path.dirname(replicaFile), exist_ok=True)
    shutil.copy2(sourceFile, replicaFile)
    log_message(f"The file {filename} was updated successfully", "Replica", logFile)

main()