package main
import("context";"fmt";"sync")
func main(){ctx,cancel:=context.WithCancel(context.Background());jobs:=make(chan int);var wg sync.WaitGroup;wg.Add(2)
for i:=0;i<2;i++{go func(){defer wg.Done();for{select{case <-ctx.Done():return;case _,ok:=<-jobs:if !ok{return}}}}()};cancel();wg.Wait();fmt.Println("stopped") }
