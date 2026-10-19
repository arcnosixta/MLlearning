import java.util.*;
public class Main {
    interface Repository { void save(int id,int score); Optional<Integer> find(int id); }
    static class MemoryRepository implements Repository {
        private final Map<Integer,Integer> values=new HashMap<>();
        public void save(int id,int score){values.put(id,score);}
        public Optional<Integer> find(int id){return Optional.ofNullable(values.get(id));}
    }
    static void record(Repository r,int id,int score) {
        if(score<0||score>100) throw new IllegalArgumentException("score");
        r.save(id,score);
    }
    public static void main(String[] args) {
        Repository r=new MemoryRepository(); record(r,1,80);
        System.out.println(r.find(1).orElseThrow());
        System.out.println(r.find(9).isEmpty());
    }
}
