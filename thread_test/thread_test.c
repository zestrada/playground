#include <stdio.h>
#include <pthread.h>


void *thread_func(void* foo) {
  int canary;
  int tls;

  asm("movl %%gs:0x14,%0\n" 
      "movl %%gs,%1\n" 
      :"=r"(canary),"=r"(tls)
  );

  printf("%x: canary value: 0x%x\n", pthread_self(), canary);
  printf("%x: tls: 0x%x\n", pthread_self(), tls);
}

int main() {
  pthread_t threads[NUM];
  int i;

  //Create all threads
  for(i=0; i<NUM; i++) {
    if(pthread_create(&threads[i], NULL, thread_func, NULL)) {
        fprintf(stderr, "Couldn't create thread %d\n", i);
    }
  }

  //Join all threads
  for(i=0; i<NUM; i++) {
    pthread_join(threads[i], NULL);
  }
  return 0;
}
