package main
import ("context"; "fmt")
func main() {
    ctx,cancel:=context.WithCancel(context.Background()); defer cancel()
    values:=make(chan int)
    go func(){ defer close(values); for _,v:=range []int{2,3,4} {
        select { case values<-v*v: case <-ctx.Done(): return }
    }}()
    total:=0; for n:=range values { total+=n }; fmt.Println(total)
}
