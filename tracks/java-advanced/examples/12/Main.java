import java.util.*;
public class Main {record Student(int id,String name){}public static void main(String[] args){Map<Integer,Student> index=new HashMap<>();for(var s:List.of(new Student(1,"Ali"),new Student(2,"Dana"))){if(index.putIfAbsent(s.id(),s)!=null)throw new IllegalArgumentException("duplicate");}System.out.println(index.get(2).name());System.out.println(index.size());}}
