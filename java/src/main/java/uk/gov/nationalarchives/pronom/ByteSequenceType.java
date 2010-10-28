
package uk.gov.nationalarchives.pronom;

import java.util.ArrayList;
import java.util.List;
import javax.xml.bind.annotation.XmlAccessType;
import javax.xml.bind.annotation.XmlAccessorType;
import javax.xml.bind.annotation.XmlAttribute;
import javax.xml.bind.annotation.XmlElement;
import javax.xml.bind.annotation.XmlSchemaType;
import javax.xml.bind.annotation.XmlType;


/**
 * <p>Java class for ByteSequenceType complex type.
 * 
 * <p>The following schema fragment specifies the expected content contained within this class.
 * 
 * <pre>
 * &lt;complexType name="ByteSequenceType">
 *   &lt;complexContent>
 *     &lt;restriction base="{http://www.w3.org/2001/XMLSchema}anyType">
 *       &lt;choice maxOccurs="unbounded" minOccurs="0">
 *         &lt;element name="SubSequence" type="{http://www.nationalarchives.gov.uk/pronom/SignatureFile}SubSequenceType"/>
 *       &lt;/choice>
 *       &lt;attribute name="Reference">
 *         &lt;simpleType>
 *           &lt;restriction base="{http://www.w3.org/2001/XMLSchema}string">
 *             &lt;enumeration value="BOFoffset"/>
 *             &lt;enumeration value="EOFoffset"/>
 *             &lt;enumeration value="IndirectBOFoffset"/>
 *             &lt;enumeration value="IndirectEOFoffset"/>
 *             &lt;enumeration value="NOoffset"/>
 *           &lt;/restriction>
 *         &lt;/simpleType>
 *       &lt;/attribute>
 *       &lt;attribute name="Endianness">
 *         &lt;simpleType>
 *           &lt;restriction base="{http://www.w3.org/2001/XMLSchema}string">
 *             &lt;enumeration value="Big-endian"/>
 *             &lt;enumeration value="Little-endian"/>
 *           &lt;/restriction>
 *         &lt;/simpleType>
 *       &lt;/attribute>
 *       &lt;attribute name="IndirectOffsetLocation" type="{http://www.w3.org/2001/XMLSchema}anySimpleType" />
 *       &lt;attribute name="IndirectOffsetLength" type="{http://www.w3.org/2001/XMLSchema}anySimpleType" />
 *     &lt;/restriction>
 *   &lt;/complexContent>
 * &lt;/complexType>
 * </pre>
 * 
 * 
 */
@XmlAccessorType(XmlAccessType.FIELD)
@XmlType(name = "ByteSequenceType", propOrder = {
    "subSequence"
})
public class ByteSequenceType {

    @XmlElement(name = "SubSequence")
    protected List<SubSequenceType> subSequence;
    @XmlAttribute(name = "Reference")
    protected String reference;
    @XmlAttribute(name = "Endianness")
    protected String endianness;
    @XmlAttribute(name = "IndirectOffsetLocation")
    @XmlSchemaType(name = "anySimpleType")
    protected String indirectOffsetLocation;
    @XmlAttribute(name = "IndirectOffsetLength")
    @XmlSchemaType(name = "anySimpleType")
    protected String indirectOffsetLength;

    /**
     * Gets the value of the subSequence property.
     * 
     * <p>
     * This accessor method returns a reference to the live list,
     * not a snapshot. Therefore any modification you make to the
     * returned list will be present inside the JAXB object.
     * This is why there is not a <CODE>set</CODE> method for the subSequence property.
     * 
     * <p>
     * For example, to add a new item, do as follows:
     * <pre>
     *    getSubSequence().add(newItem);
     * </pre>
     * 
     * 
     * <p>
     * Objects of the following type(s) are allowed in the list
     * {@link SubSequenceType }
     * 
     * 
     */
    public List<SubSequenceType> getSubSequence() {
        if (subSequence == null) {
            subSequence = new ArrayList<SubSequenceType>();
        }
        return this.subSequence;
    }

    /**
     * Gets the value of the reference property.
     * 
     * @return
     *     possible object is
     *     {@link String }
     *     
     */
    public String getReference() {
        return reference;
    }

    /**
     * Sets the value of the reference property.
     * 
     * @param value
     *     allowed object is
     *     {@link String }
     *     
     */
    public void setReference(String value) {
        this.reference = value;
    }

    /**
     * Gets the value of the endianness property.
     * 
     * @return
     *     possible object is
     *     {@link String }
     *     
     */
    public String getEndianness() {
        return endianness;
    }

    /**
     * Sets the value of the endianness property.
     * 
     * @param value
     *     allowed object is
     *     {@link String }
     *     
     */
    public void setEndianness(String value) {
        this.endianness = value;
    }

    /**
     * Gets the value of the indirectOffsetLocation property.
     * 
     * @return
     *     possible object is
     *     {@link String }
     *     
     */
    public String getIndirectOffsetLocation() {
        return indirectOffsetLocation;
    }

    /**
     * Sets the value of the indirectOffsetLocation property.
     * 
     * @param value
     *     allowed object is
     *     {@link String }
     *     
     */
    public void setIndirectOffsetLocation(String value) {
        this.indirectOffsetLocation = value;
    }

    /**
     * Gets the value of the indirectOffsetLength property.
     * 
     * @return
     *     possible object is
     *     {@link String }
     *     
     */
    public String getIndirectOffsetLength() {
        return indirectOffsetLength;
    }

    /**
     * Sets the value of the indirectOffsetLength property.
     * 
     * @param value
     *     allowed object is
     *     {@link String }
     *     
     */
    public void setIndirectOffsetLength(String value) {
        this.indirectOffsetLength = value;
    }

}
