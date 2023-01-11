#include <stdlib.h>
#include <stdio.h>
#include <sys/ipc.h>
#include <sys/shm.h>

int main(int argc, char **argv) {
    //When running in the shared object we'll get the ID from the env
    //Still need to test that with the fuzzer and qemu plugin
    int shmid = atoi(argv[1]);
    char *bytes;
    struct shmid_ds buf;
    bytes = shmat(shmid, NULL, SHM_RDONLY);
    shmctl(shmid, IPC_STAT, &buf);
    printf("shm.segsz: %lu\n",buf.shm_segsz);

    for(int i=0; i<4; i++) {
        printf("shm[%d]: 0x%x\n",i,bytes[i]);
    }
    shmdt(bytes);
    return 0;
}
