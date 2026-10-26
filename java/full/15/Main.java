import java.util.function.*;
public class Main {
    public static void main(String[] args) {
        Predicate<Integer> positive = n -> n > 0;
        Predicate<Integer> even = n -> n % 2 == 0;
        Function<Integer, Integer> twice = n -> n * 2;
        Function<Integer, Integer> plusOne = n -> n + 1;
        System.out.println(positive.and(even).test(4));
        System.out.println(twice.andThen(plusOne).apply(3));
        System.out.println(twice.compose(plusOne).apply(3));
    }
}
