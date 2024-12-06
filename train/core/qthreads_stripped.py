from PySide6.QtCore import QThreadPool, QThread
from train.core.train import Train
from train.core.train_model import Train_Model
from train.train_controller.train_controller_class import TrainController


class QThreadPool_Data():

    obj_count = 0
    MAX_THREADS = QThreadPool.globalInstance().maxThreadCount()

    def __init__(self, pool : QThreadPool, index_of_first_obj : int) -> None:
        self.threadpool = pool
        self.index_of_first_obj = index_of_first_obj
        self.filled = False
        self.objects = [None for _ in range(QThreadPool_Data.MAX_THREADS)]

        QThreadPool_Data.obj_count +=1

    def remove(self) -> None:
        del self

    def __del__(self) -> None:
        print("[TRAIN]: QThreadPool_Data deleted.")
        QThreadPool_Data.obj_count -= 1


class QThreadPool_Manager():

    '''
    This property holds the maximum number of threads used by the thread pool. 
    This property will default to the value of idealThreadCount() (member of QThread class) 
    at the moment the QThreadPool object is created.
    '''
    MAX_THREADS = QThreadPool.globalInstance().maxThreadCount()

    def __init__(self) -> None:

        self.total_obj_count = 0                # keeps track of the total number of objects that have been created.
                                                # does not matter whether the objects have been deleted.
        self.running_obj_count = 0              # keeps count of the objects that are running in threads. 
        
        self.threadpools : QThreadPool_Data = list()

    # Return a reference to the most recent object that was added.
    def peek_tail(self):
        return self.threadpools[-1].objects[(self.total_obj_count-1) % QThreadPool_Manager.MAX_THREADS]
    
    # Return a reference to the object at an index.
    # The index is what the object was assigned with - assigned with the current value of total_obj_count. 
    def peek_idx(self, idx : int):

        # Find which threadpool the object is in
        num = self.__find_threadpool(idx)

        # Return if the object cant be found        
        if num is None: return None
        
        # Get the object and return it
        return self.threadpools[num].objects[idx % QThreadPool_Manager.MAX_THREADS]
    
    def peek_model(self, idx : int):
        # Find which threadpool the object is in
        num = self.__find_threadpool(idx)

        # Return if the object cant be found        
        if num is None: return None

        obj = self.threadpools[num].objects[idx % QThreadPool_Manager.MAX_THREADS]
        if type(obj) == Train:
            return obj.train_model


    def peek_controller(self, idx: int):
        # Find which threadpool the object is in
        num = self.__find_threadpool(idx)

        # Return if the object cant be found        
        if num is None: return None

        obj = self.threadpools[num].objects[idx % QThreadPool_Manager.MAX_THREADS]
        if type(obj) == Train:
            return obj.controller

    
    def get_running_obj_count(self) -> int:
        return self.running_obj_count
    
    def get_total_obj_count(self) -> int:
        return self.total_obj_count

    # Add a thread
    # param: object
    # object has to be a derived from a Qrunnable and must have a run function (overrides the Qrunnable run function)
    # object should have a __del__ function implemented so that we know if remove_thread is actually deleting the object.
    def add_thread(self, object) -> None:
        
        # Create a new threadpool once object count reached a multiple of max threads
        if((self.total_obj_count % QThreadPool_Manager.MAX_THREADS) == 0):
            self.__add_threadpool()

        # Print the train's number
        print(f"[TRAIN]: Train/Thread Count: {self.total_obj_count}")

        # Start the thread - automatically calls the object's run() function
        self.threadpools[-1].threadpool.start(object)

        # Store the object object in QThreadPool_Data
        self.threadpools[-1].objects[self.total_obj_count % QThreadPool_Manager.MAX_THREADS] = object

       # Check if the object we just added takes up the last available thread in the threadpool.
       # Previously, because its using total_obj_count, it ignores trains that were added but then already removed in
       # the threadpool. 
        if((self.total_obj_count % QThreadPool_Manager.MAX_THREADS) == (QThreadPool_Manager.MAX_THREADS-1)):
            self.threadpools[-1].filled = True
            print(f"[TRAIN]: threadpool {len(self.threadpools) -1} was marked as filled")

        # Increment the train count.
        self.total_obj_count += 1
        self.running_obj_count += 1
    
    
    # Remove a thread
    def remove_thread(self, idx: int):

        # Search list for where the index would be.
        num = self.__find_threadpool(idx)

        # Error checking
        if num == None:
            print("[TRAIN]: Could not find valid threadpool for index {idx}. Returning.")
            return

        # Print results
        # print(f"[TRAIN]: Calculated threadpool {num} for index {idx}.")
        
        # Clean up thread and objects if it exists
        if self.threadpools[num].objects[idx % QThreadPool_Manager.MAX_THREADS] != None:
            try:
                self.threadpools[num].objects[idx % QThreadPool_Manager.MAX_THREADS].delete()
            except AttributeError:
                print("[TRAIN]: QRUNNABLE SHOULD HAVE A delete() METHOD THAT STOPS THE WHILE LOOP!")
            self.threadpools[num].objects[idx % QThreadPool_Manager.MAX_THREADS] = None

            # Decrement train count
            self.running_obj_count -= 1
        else:
            print("[TRAIN]: Obj has already been deleted.")
            return
        
        # Active thread count doesn't update right away, takes a little bit.
        # So if its currently 1, it will be zero in a bit but the threadpool can be deleted now
        # because the object has already been deleted.
        # print(f"[TRAIN]: New active thread count: {self.threadpools[num].threadpool.activeThreadCount()-1}")

        # If the threadpool was filled and active thread count is now 1 or
        # 0 (in case it did update), remove threadpool. 
        if (self.threadpools[num].threadpool.activeThreadCount() <= 1) and (self.threadpools[num].filled):
            self.__remove_threadpool(num)

        # Because activethreadcount doesnt always update right away, check for any stray threadpools that need to be deleted.
        # Delete backwards so as not to affect indexing
        for i in range(len(self.threadpools)-1, -1, -1):
            if (self.threadpools[i].threadpool.activeThreadCount() == 0) and self.threadpools[i].filled:
                self.__remove_threadpool(i)

    # Add a threadpool
    def __add_threadpool(self) -> None:

        print("[TRAIN]: Creating threadpool.")

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
        print(f"[TRAIN]: New pool's priority: {new_pool.threadPriority()}")
        print(f"[TRAIN]: Multithreading with maximum {new_pool.maxThreadCount()} threads")

        # Check if there is a mismatch between the originally stored MAX_THREAD num and the 
        # max thread of the new pool.
        if new_pool.maxThreadCount() != QThreadPool_Manager.MAX_THREADS:
            print(f"[TRAIN]: WARNING: CORE COUNT MISMATCH. CAN NO LONGER REACH {QThreadPool_Manager.MAX_THREADS} THREADS!!")

        # Append the new threadpool to threadpool list.
        self.threadpools.append(QThreadPool_Data(new_pool, self.total_obj_count))


    # Remove a threadpool
    def __remove_threadpool(self, idx: int) -> None:
        
        print(f"[TRAIN]: Removing Threadpool {idx}.")

        # Tell QThreadPool_Data is clean up itself.
        self.threadpools[idx].remove()

        # Delete it
        del self.threadpools[idx]


    # Find threadpool that the object specified by the index is in
    def __find_threadpool(self, idx: int) -> int:

        # Check if valid index
        if idx < 0 or idx >= (self.threadpools[-1].index_of_first_obj + self.MAX_THREADS):
            return None

        # Find the threadpool that the train index exists in
        for i in range(0, len(self.threadpools)):
            if self.threadpools[i].index_of_first_obj > idx:
                return i-1
        
        # If not found, that means it is the last index
        return len(self.threadpools) - 1
            

    # Print active thread counts for each threadpool
    def print_active_threads_all(self) -> None:
        for pool in self.threadpools:
            print(f"[TRAIN]: object idx for threadpool: {pool.index_of_first_obj} and active thread count for threadpool: {pool.threadpool.activeThreadCount()}")

    # Print a list of all the train objects
    def print_obj_list(self) -> None:
        print("[TRAIN]: ")
        print("[TRAIN]: ############ BEGIN OBJECT LIST ############")
        print("[TRAIN]: ")
        for pool in self.threadpools:
            print(pool.objects)
            print("[TRAIN]: ")
        print("[TRAIN]: ############ END OBJECT LIST ############")
        print("[TRAIN]: ")
        