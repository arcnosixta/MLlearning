import java.util.concurrent.CompletableFuture;
public class Main {public static void main(String[] args){var price=CompletableFuture.completedFuture(100);var discount=CompletableFuture.completedFuture(15);System.out.println(price.thenCombine(discount,(p,d)->p-d).join());System.out.println(CompletableFuture.<Integer>failedFuture(new IllegalStateException()).exceptionally(e->0).join());}}
