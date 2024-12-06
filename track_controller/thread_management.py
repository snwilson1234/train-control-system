from PySide6.QtCore import QThreadPool, QThread
from track_controller.wayside_controller_ui import PLCOutput


class QThreadPool_Data():

    obj_count = 0
    MAX_THREADS = QThreadPool.globalInstance().maxThreadCount()

    def __init__(self, pool : QThreadPool, first_program_num : int) -> None:
        self.threadpool = pool
        self.first_program_num = first_program_num
        self.filled = False
        self.programs = [None for _ in range(QThreadPool_Data.MAX_THREADS)]

        QThreadPool_Data.obj_count +=1

    def remove(self) -> None:
        del self

    def __del__(self) -> None:
        print("[TRACK CONTROLLER]: QThreadPool_Data deleted.")
        QThreadPool_Data.obj_count -= 1


class QThreadPool_Manager():

    '''
    This property holds the maximum number of threads used by the thread pool. 
    This property will default to the value of idealThreadCount() (member of QThread class) 
    at the moment the QThreadPool object is created.
    '''
    MAX_THREADS = QThreadPool.globalInstance().maxThreadCount()

    def __init__(self) -> None:

        self.program_count = 0                # keeps track of the total programs that have been created
        self.running_program_count = 0       # keeps count of programs that are actively running
        self.threadpools : QThreadPool_Data = list()

    
    def get_running_program_count(self) -> int:
        return self.running_program_count

    # Add a thread
    def add_thread(self) -> None:
        
        # Create a new threadpool once program count reached a multiple of 12
        if((self.program_count % QThreadPool_Manager.MAX_THREADS) == 0):
            self.__add_threadpool()

        # Create new program and assign it the next number (=program_count)
        

        # Print the program's number
        print(f"[TRACK CONTROLLER]: Program/Thread Count: {program_and_ui.program.get_identifier()}")

        # Start the thread - automatically calls the object's run() function
        self.threadpools[-1].threadpool.start(program_and_ui.program)

        # Store the program object in QThreadPool_Data
        self.threadpools[-1].programs[self.program_count % QThreadPool_Manager.MAX_THREADS] = program_and_ui

       # Check if the program we just added takes up the last available thread in the threadpool.
       # Because its using program_count, it ignores programs that were added but then already removed in
       # the threadpool. 
        if((self.program_count % QThreadPool_Manager.MAX_THREADS) == (QThreadPool_Manager.MAX_THREADS-1)):
            self.threadpools[-1].filled = True
            print(f"[TRACK CONTROLLER]: threadpool {len(self.threadpools) -1} was marked as filled")

        # Increment the program count.
        self.program_count += 1
        self.running_program_count += 1
    
    
    # Remove a thread
    def remove_thread(self, idx: int):

        # Search list for where the index would be.
        num = self.__find_threadpool(idx)

        # Error checking
        if num == None:
            print("[TRACK CONTROLLER]: Could not find valid threadpool for index {idx}. Returning.")
            return

        # Print results
        print(f"[TRACK CONTROLLER]: Calculated threadpool {num} for index {idx}.")
        
        # Clean up thread and objects if it exists
        if self.threadpools[num].programs[idx % QThreadPool_Manager.MAX_THREADS] != None:
            self.threadpools[num].programs[idx % QThreadPool_Manager.MAX_THREADS].program.delete()
            self.threadpools[num].programs[idx % QThreadPool_Manager.MAX_THREADS].delete()
            self.threadpools[num].programs[idx % QThreadPool_Manager.MAX_THREADS] = None

            # Decrement program count
            self.running_program_count -= 1
        else:
            print("[TRACK CONTROLLER]: Program has already been deleted.")
            return
        
        # Active thread count doesn't update right away, takes a little bit.
        # So if its currently 1, it will be zero in a bit but the threadpool can be deleted now
        # because the object has already been deleted.
        print(f"[TRACK CONTROLLER]: New active thread count: {self.threadpools[num].threadpool.activeThreadCount()-1}")

        # If the threadpool was filled and active thread count is now 1 or
        # 0 (in case it did update), remove threadpool. 
        if (self.threadpools[num].threadpool.activeThreadCount() <= 1) and \
            (self.threadpools[num].filled):
            self.__remove_threadpool(num)

    # Add a threadpool
    def __add_threadpool(self) -> None:

        print("[TRACK CONTROLLER]: Creating threadpool.")

        # Create threadpool
        new_pool = QThreadPool()

        # Set thread timeout to 1 msec after thread goes idle.
        new_pool.setExpiryTimeout(1)

        '''
        from https://doc.qt.io/qtforpython-6/PySide6/QtCore/QThread.html#PySide6.QtCore.PySide6.QtCore.QThread.Priority
        QThread.IdlePriority            scheduled only when no other threads are running.
        QThread.LowestPriority          scheduled less often than LowPriority.
        QThread.LowPriority             scheduled less often than NormalPriority.
        QThread.NormalPriority          the default priority of the operating system.
        QThread.HighPriority            scheduled more often than NormalPriority.
        QThread.HighestPriority         scheduled more often than HighPriority.
        QThread.TimeCriticalPriority    scheduled as often as possible.
        QThread.InheritPriority         use the same priority as the creating thread. This is the default.        
        '''
        new_pool.setThreadPriority(QThread.Priority.NormalPriority)

        # Print new thread data
        print(f"[TRACK CONTROLLER]: New pool's priority: {new_pool.threadPriority()}")
        print(f"[TRACK CONTROLLER]: Multithreading with maximum {new_pool.maxThreadCount()} threads")

        # Check if there is a mismatch between the originally stored MAX_THREAD num and the 
        # max thread of the new pool.
        if new_pool.maxThreadCount() != QThreadPool_Manager.MAX_THREADS:
            print(f"[TRACK CONTROLLER]: WARNING: CORE COUNT MISMATCH. CAN NO LONGER REACH {QThreadPool_Manager.MAX_THREADS} THREADS!!")

        # Append the new threadpool to threadpool list.
        self.threadpools.append(QThreadPool_Data(new_pool, self.program_count))


    # Remove a threadpool
    def __remove_threadpool(self, idx: int) -> None:
        
        print("[TRACK CONTROLLER]: Removing Threadpool {idx}.")

        # Tell QThreadPool_Data is clean up itself.
        self.threadpools[idx].remove()

        # Delete it
        del self.threadpools[idx]


    # Find threadpool that the object specified by the index is in
    def __find_threadpool(self, idx: int) -> int:

        # Check if valid index
        if idx < 0 or idx >= (self.threadpools[-1].first_program_num + self.MAX_THREADS):
            return None

        # Find the threadpool that the program index exists in
        for i in range(0, len(self.threadpools)):
            if self.threadpools[i].first_program_num > idx:
                return i-1
        
        # If not found, that means it is the last index
        return len(self.threadpools) - 1
            

    # Print active thread counts for each threadpool
    def print_active_threads_all(self) -> None:
        for pool in self.threadpools:
            print(f"[TRACK CONTROLLER]: program idx for threadpool: {pool.first_program_num} and active thread count for threadpool: {pool.threadpool.activeThreadCount()}")

    # Print a list of all the program objects running
    def print_programs_list(self) -> None:
        print("[TRACK CONTROLLER]: ")
        print("[TRACK CONTROLLER]: ############ BEGIN PROGRAMS LIST ############")
        print("[TRACK CONTROLLER]: ")
        for pool in self.threadpools:
            print(pool.programs)
            print("[TRACK CONTROLLER]: ")
        print("[TRACK CONTROLLER]: ############ END PROGRAMS LIST ############")
        print("[TRACK CONTROLLER]: ")
        