
package uk.gov.nationalarchives.pronom;

import java.math.BigInteger;
import javax.xml.bind.JAXBElement;
import javax.xml.bind.annotation.XmlElementDecl;
import javax.xml.bind.annotation.XmlRegistry;
import javax.xml.namespace.QName;


/**
 * This object contains factory methods for each 
 * Java content interface and Java element interface 
 * generated in the uk.gov.nationalarchives.pronom package. 
 * <p>An ObjectFactory allows you to programatically 
 * construct new instances of the Java representation 
 * for XML content. The Java representation of XML 
 * content can consist of schema derived interfaces 
 * and classes representing the binding of schema 
 * type definitions, element declarations and model 
 * groups.  Factory methods for each of these are 
 * provided in this class.
 * 
 */
@XmlRegistry
public class ObjectFactory {

    private final static QName _SubSequenceTypeLeftFragment_QNAME = new QName("http://www.nationalarchives.gov.uk/pronom/SignatureFile", "LeftFragment");
    private final static QName _SubSequenceTypeShift_QNAME = new QName("http://www.nationalarchives.gov.uk/pronom/SignatureFile", "Shift");
    private final static QName _SubSequenceTypeRightFragment_QNAME = new QName("http://www.nationalarchives.gov.uk/pronom/SignatureFile", "RightFragment");
    private final static QName _FileFormatTypeExtension_QNAME = new QName("http://www.nationalarchives.gov.uk/pronom/SignatureFile", "Extension");
    private final static QName _FileFormatTypeHasPriorityOverFileFormatID_QNAME = new QName("http://www.nationalarchives.gov.uk/pronom/SignatureFile", "HasPriorityOverFileFormatID");
    private final static QName _FileFormatTypeInternalSignatureID_QNAME = new QName("http://www.nationalarchives.gov.uk/pronom/SignatureFile", "InternalSignatureID");

    /**
     * Create a new ObjectFactory that can be used to create new instances of schema derived classes for package: uk.gov.nationalarchives.pronom
     * 
     */
    public ObjectFactory() {
    }

    /**
     * Create an instance of {@link GetSignatureFileV1Response }
     * 
     */
    public GetSignatureFileV1Response createGetSignatureFileV1Response() {
        return new GetSignatureFileV1Response();
    }

    /**
     * Create an instance of {@link SignatureFileType.InternalSignatureCollection }
     * 
     */
    public SignatureFileType.InternalSignatureCollection createSignatureFileTypeInternalSignatureCollection() {
        return new SignatureFileType.InternalSignatureCollection();
    }

    /**
     * Create an instance of {@link SigFile }
     * 
     */
    public SigFile createSigFile() {
        return new SigFile();
    }

    /**
     * Create an instance of {@link GetSignatureFileV1 }
     * 
     */
    public GetSignatureFileV1 createGetSignatureFileV1() {
        return new GetSignatureFileV1();
    }

    /**
     * Create an instance of {@link GetSignatureFileVersionV1Response }
     * 
     */
    public GetSignatureFileVersionV1Response createGetSignatureFileVersionV1Response() {
        return new GetSignatureFileVersionV1Response();
    }

    /**
     * Create an instance of {@link FileFormatType }
     * 
     */
    public FileFormatType createFileFormatType() {
        return new FileFormatType();
    }

    /**
     * Create an instance of {@link SignatureFileType }
     * 
     */
    public SignatureFileType createSignatureFileType() {
        return new SignatureFileType();
    }

    /**
     * Create an instance of {@link ShiftType }
     * 
     */
    public ShiftType createShiftType() {
        return new ShiftType();
    }

    /**
     * Create an instance of {@link FragmentType }
     * 
     */
    public FragmentType createFragmentType() {
        return new FragmentType();
    }

    /**
     * Create an instance of {@link InternalSignatureType }
     * 
     */
    public InternalSignatureType createInternalSignatureType() {
        return new InternalSignatureType();
    }

    /**
     * Create an instance of {@link Version }
     * 
     */
    public Version createVersion() {
        return new Version();
    }

    /**
     * Create an instance of {@link SignatureFileType.FileFormatCollection }
     * 
     */
    public SignatureFileType.FileFormatCollection createSignatureFileTypeFileFormatCollection() {
        return new SignatureFileType.FileFormatCollection();
    }

    /**
     * Create an instance of {@link SubSequenceType }
     * 
     */
    public SubSequenceType createSubSequenceType() {
        return new SubSequenceType();
    }

    /**
     * Create an instance of {@link ByteSequenceType }
     * 
     */
    public ByteSequenceType createByteSequenceType() {
        return new ByteSequenceType();
    }

    /**
     * Create an instance of {@link GetSignatureFileVersionV1 }
     * 
     */
    public GetSignatureFileVersionV1 createGetSignatureFileVersionV1() {
        return new GetSignatureFileVersionV1();
    }

    /**
     * Create an instance of {@link JAXBElement }{@code <}{@link FragmentType }{@code >}}
     * 
     */
    @XmlElementDecl(namespace = "http://www.nationalarchives.gov.uk/pronom/SignatureFile", name = "LeftFragment", scope = SubSequenceType.class)
    public JAXBElement<FragmentType> createSubSequenceTypeLeftFragment(FragmentType value) {
        return new JAXBElement<FragmentType>(_SubSequenceTypeLeftFragment_QNAME, FragmentType.class, SubSequenceType.class, value);
    }

    /**
     * Create an instance of {@link JAXBElement }{@code <}{@link ShiftType }{@code >}}
     * 
     */
    @XmlElementDecl(namespace = "http://www.nationalarchives.gov.uk/pronom/SignatureFile", name = "Shift", scope = SubSequenceType.class)
    public JAXBElement<ShiftType> createSubSequenceTypeShift(ShiftType value) {
        return new JAXBElement<ShiftType>(_SubSequenceTypeShift_QNAME, ShiftType.class, SubSequenceType.class, value);
    }

    /**
     * Create an instance of {@link JAXBElement }{@code <}{@link FragmentType }{@code >}}
     * 
     */
    @XmlElementDecl(namespace = "http://www.nationalarchives.gov.uk/pronom/SignatureFile", name = "RightFragment", scope = SubSequenceType.class)
    public JAXBElement<FragmentType> createSubSequenceTypeRightFragment(FragmentType value) {
        return new JAXBElement<FragmentType>(_SubSequenceTypeRightFragment_QNAME, FragmentType.class, SubSequenceType.class, value);
    }

    /**
     * Create an instance of {@link JAXBElement }{@code <}{@link String }{@code >}}
     * 
     */
    @XmlElementDecl(namespace = "http://www.nationalarchives.gov.uk/pronom/SignatureFile", name = "Extension", scope = FileFormatType.class)
    public JAXBElement<String> createFileFormatTypeExtension(String value) {
        return new JAXBElement<String>(_FileFormatTypeExtension_QNAME, String.class, FileFormatType.class, value);
    }

    /**
     * Create an instance of {@link JAXBElement }{@code <}{@link BigInteger }{@code >}}
     * 
     */
    @XmlElementDecl(namespace = "http://www.nationalarchives.gov.uk/pronom/SignatureFile", name = "HasPriorityOverFileFormatID", scope = FileFormatType.class)
    public JAXBElement<BigInteger> createFileFormatTypeHasPriorityOverFileFormatID(BigInteger value) {
        return new JAXBElement<BigInteger>(_FileFormatTypeHasPriorityOverFileFormatID_QNAME, BigInteger.class, FileFormatType.class, value);
    }

    /**
     * Create an instance of {@link JAXBElement }{@code <}{@link BigInteger }{@code >}}
     * 
     */
    @XmlElementDecl(namespace = "http://www.nationalarchives.gov.uk/pronom/SignatureFile", name = "InternalSignatureID", scope = FileFormatType.class)
    public JAXBElement<BigInteger> createFileFormatTypeInternalSignatureID(BigInteger value) {
        return new JAXBElement<BigInteger>(_FileFormatTypeInternalSignatureID_QNAME, BigInteger.class, FileFormatType.class, value);
    }

}
