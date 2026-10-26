import java.util.*;
public class Main {
    static <T> void copy(List<? extends T> source, List<? super T> target) {
        for (T value : source) target.add(value);
    }
    public static void main(String[] args) {
        List<Integer> source = List.of(2, 4, 6);
        List<Number> target = new ArrayList<>();
        copy(source, target);
        System.out.println(target);
        System.out.println(source.size());
    }
}
