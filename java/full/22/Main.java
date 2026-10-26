import java.io.StringReader;
import javax.xml.XMLConstants;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.xpath.*;
import org.xml.sax.InputSource;
public class Main {
    public static void main(String[] args) throws Exception {
        var factory = DocumentBuilderFactory.newInstance();
        factory.setNamespaceAware(true);
        factory.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING, true);
        factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
        factory.setAttribute(XMLConstants.ACCESS_EXTERNAL_DTD, "");
        factory.setAttribute(XMLConstants.ACCESS_EXTERNAL_SCHEMA, "");
        factory.setXIncludeAware(false);
        factory.setExpandEntityReferences(false);
        String xml = "<students><student id='1'>Aida</student><student id='2'>Arman</student></students>";
        var document = factory.newDocumentBuilder().parse(new InputSource(new StringReader(xml)));
        var xpath = XPathFactory.newInstance().newXPath();
        System.out.println(xpath.evaluate("count(/students/student)", document));
        System.out.println(xpath.evaluate("/students/student[@id='1']/text()", document));
    }
}
