import java.util.*;
public class Main {
    public static void main(String[] args) {
        List<Integer> marks = List.of(40, 90, 70, 30);
        List<Integer> passed = marks.stream().filter(x -> x >= 50).sorted().toList();
        int total = marks.stream().mapToInt(Integer::intValue).sum();
        System.out.println(passed);
        System.out.println(total);
    }
}
