import java.util.*;
public class Main {
    static double sum(List<? extends Number> values) {
        double total=0; for(Number n:values) total+=n.doubleValue(); return total;
    }
    static void addIds(List<? super Integer> values) { values.add(7); }
    public static void main(String[] args) {
        List<Number> target=new ArrayList<>(); addIds(target);
        System.out.println(sum(List.of(2,3,4)));
        System.out.println(target);
    }
}
