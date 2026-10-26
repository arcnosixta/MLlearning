import java.util.List;
import org.testng.Assert;
import org.testng.annotations.*;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
public class MainTest {
    private static final Logger LOG = LogManager.getLogger(MainTest.class);
    @DataProvider(name = "averages")
    public Object[][] averages() {
        return new Object[][] {{List.of(0), 0.0}, {List.of(100), 100.0}, {List.of(2, 3), 2.5}};
    }
    @Test(dataProvider = "averages")
    public void average(List<Integer> grades, double expected) {
        Assert.assertEquals(Main.average(grades).orElseThrow(), expected, 0.000001);
        LOG.info("validated grades={}", grades.size());
    }
    @Test public void emptyIsAbsent() { Assert.assertTrue(Main.average(List.of()).isEmpty()); }
    @Test public void rejectsLow() { Assert.expectThrows(IllegalArgumentException.class, () -> Main.average(List.of(-1))); }
    @Test public void rejectsHigh() { Assert.expectThrows(IllegalArgumentException.class, () -> Main.average(List.of(101))); }
}
