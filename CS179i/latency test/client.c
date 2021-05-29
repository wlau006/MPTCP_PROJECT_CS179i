#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netdb.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <arpa/inet.h>
#include <netinet/tcp.h>
#include <time.h>


static char *rand_string(char *str, int size)
{
    const char charset[] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJK...";
    if (size) {
        --size;
        for (int n = 0; n < size; n++) {
            int key = rand() % (int) (sizeof charset - 1);
            str[n] = charset[key];
        }
        str[size] = '\0';
    }
    return str;
}
 
int main(void)
{
  int sockfd = 0,n = 0;
  char recvBuff[1024];
  struct sockaddr_in serv_addr;
 
  memset(recvBuff, '0' ,sizeof(recvBuff));
  if((sockfd = socket(AF_INET, SOCK_STREAM, 0))< 0)
    {
      printf("\n Error : Could not create socket \n");
      return 1;
    }
 
  serv_addr.sin_family = AF_INET;
  serv_addr.sin_port = htons(5000);
  serv_addr.sin_addr.s_addr = inet_addr("10.0.0.2");
  int enable = 1;
  setsockopt(sockfd, SOL_TCP, 42, &enable, sizeof(enable));
 
  if(connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr))<0)
    {
      printf("\n Error : Connect Failed \n");
      return 1;
    }

  int a;
  unsigned c;
  char* word = "1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111";
  time_t start, end;

  for (c = 1; c <= 1000; c++) {
        word = rand_string(word,word.size());
        start = time(NULL);
        send(sockfd , word , strlen(word) , 0 );
        printf("Hello");
    while((n = read(sockfd, recvBuff, sizeof(recvBuff)-1)) > 0)
      {
        recvBuff[n] = 0;  
        end = time(NULL);
        printf("Sent word of length %ld with RTT of %f\n", strlen(word), difftime(end,start));
      }
  }
  return 0;
}
