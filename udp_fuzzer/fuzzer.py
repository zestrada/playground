#!/usr/bin/env python3
from pylibafl import libafl
import ctypes
import socket

port = 6600
host = "127.0.0.1"

#example seeds obtained from angr
seeds = [b'\0\0',b'\xfb\x00\x00T\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',b'\x00\x00\x00T\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00']

#Seeds to play with the UDP server
#seeds = [b'sekretsquirrep']

#Just something to play with
tokens = [b"\x00\x00\x00\x05AAAAA", b"\x00\x05AAAAA", b"\x05\x00\x00\x00AAAAA", b"\x05\x00AAAAA", b"\x09\x00\x00\x00AAAAA", b"\x08\x00AAAAAA"]

class UDPFeedback(libafl.BaseFeedback):
    #Not surprised if this is default behavior
    def is_interesting(self, state, mgr, input, observers, exit_kind):
        return libafl.ExitKind.is_crash(exit_kind)

class UDPExecutor(libafl.BaseExecutor):
    def __init__(self, host, port, observers: libafl.ObserversTuple):
        self.o = observers
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = host
        self.port = port
        self.s.connect((self.host, self.port))

    def observers(self):
        return self.o

    def run_target(self, fuzzer, state, mgr, input) -> libafl.ExitKind:
        self.s.sendall(input)
        self.s.settimeout(0.02)
        data = None
        try:
            data = self.s.recvfrom(1024)
        except socket.timeout:
        #Timeout
            pass
        if data is not None:
            print(f"Saw response: {data} to {input}")
            #Add input to state
            return libafl.ExitKind.crash()
        return libafl.ExitKind.ok()

#Base on FooObserver of example
class CountObserver(libafl.BaseObserver):
    def __init__(self):
        self.n = 0

    def name(self):
        return "Count"

    def pre_exec(self, state, input):
        if self.n % 10000 == 0:
            print("TICK!", self.n, input)
        self.n += 1

libc = ctypes.cdll.LoadLibrary("libc.so.6")

area_ptr = libc.calloc(1, 4096)
observer = libafl.StdMapObserverI8("udpmap", area_ptr, 4096)
observers = libafl.ObserversTuple(
    [observer.as_map_observer().as_observer(), CountObserver().as_observer()]
)

rand = libafl.StdRand.with_current_nanos()

m = observer.as_map_observer()

feedback = libafl.feedback_or(libafl.MaxMapFeedbackI8(m).as_feedback(), UDPFeedback().as_feedback())

input_corpus = libafl.InMemoryCorpus().as_corpus()

#Not sure we want to OR on this when we actually implement coverage
objective = libafl.feedback_or_fast(
            UDPFeedback().as_feedback(), libafl.MaxMapFeedbackI8(m).as_feedback()
            )

output_corpus = libafl.InMemoryCorpus().as_corpus()

state = libafl.StdState(
    rand.as_rand(),
    input_corpus,
    output_corpus,
    feedback,
    objective,
)

executor = UDPExecutor(host, port, observers)
stage = libafl.StdMutationalStage(libafl.StdHavocMutator().as_mutator())

monitor = libafl.SimpleMonitor(lambda s: print(s))
mgr = libafl.SimpleEventManager(monitor.as_monitor())

stage_tuple_list = libafl.StagesTuple([stage.as_stage()])
fuzzer = libafl.StdFuzzer(feedback, objective)

for seed in seeds:
    fuzzer.add_input(state, executor.as_executor(), mgr.as_manager(), seed)

#import IPython; IPython.embed()
try:
    fuzzer.fuzz_loop(executor.as_executor(), state, mgr.as_manager(), stage_tuple_list)
except KeyboardInterrupt:
    #This doesn't work
    print("ctrl+c!")
    print(f"output corpus of size: {output_corpus.count()}")
    for i in range(output_corpus.count()): 
        print(output_corpus.get(i))
