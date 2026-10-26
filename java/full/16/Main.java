import java.util.*;
import java.util.stream.Collectors;
public class Main {
    public static void main(String[] args) {
        List<Integer> grades = List.of(90, 50, 90, 75);
        System.out.println(grades.stream().filter(n -> n >= 60).distinct().sorted().toList());
        var groups = grades.stream().collect(Collectors.groupingBy(n -> n >= 60, TreeMap::new, Collectors.counting()));
        System.out.println(groups);
        System.out.println(grades.stream().mapToInt(Integer::intValue).average().orElseThrow());
    }
}
