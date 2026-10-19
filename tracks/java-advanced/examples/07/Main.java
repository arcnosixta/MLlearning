public class Main {
record Money(int cents){Money{if(cents<0)throw new IllegalArgumentException("negative");}}
sealed interface Result permits Paid,Rejected{}
record Paid(Money value) implements Result{}
record Rejected(String reason) implements Result{}
public static void main(String[] args){System.out.println(new Money(100).equals(new Money(100)));Result r=new Paid(new Money(100));System.out.println(r instanceof Paid);}}
