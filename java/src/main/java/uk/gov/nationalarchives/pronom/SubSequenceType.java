
package uk.gov.nationalarchives.pronom;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;
import javax.xml.bind.JAXBElement;
import javax.xml.bind.annotation.XmlAccessType;
import javax.xml.bind.annotation.XmlAccessorType;
import javax.xml.bind.annotation.XmlAttribute;
import javax.xml.bind.annotation.XmlElement;
import javax.xml.bind.annotation.XmlElementRef;
import javax.xml.bind.annotation.XmlElementRefs;
import javax.xml.bind.annotation.XmlType;


/**
 * <p>Java class for SubSequenceType complex type.
 * 
 * <p>The following schema fragment specifies the expected content contained within this class.
 * 
 * <pre>
 * &lt;complexType name="SubSequenceType">
 *   &lt;complexContent>
 *     &lt;restriction base="{http://www.w3.org/2001/XMLSchema}anyType">
 *       &lt;sequence>
 *         &lt;element name="Sequence" type="{http://www.nationalarchives.gov.uk/pronom/SignatureFile}HexBytes"/>
 *         &lt;element name="DefaultShift" type="{http://www.w3.org/2001/XMLSchema}integer"/>
 *         &lt;choice maxOccurs="unbounded" minOccurs="0">
 *           &lt;element name="Shift" type="{http://www.nationalarchives.gov.uk/pronom/SignatureFile}ShiftType"/>
 *           &lt;element name="LeftFragment" type="{http://www.nationalarchives.gov.uk/pronom/SignatureFile}FragmentType"/>
 *           &lt;element name="RightFragment" type="{http://www.nationalarchives.gov.uk/pronom/SignatureFile}FragmentType"/>
 *         &lt;/choice>
 *       &lt;/sequence>
 *       &lt;attribute name="Position" use="required" type="{http://www.w3.org/2001/XMLSchema}integer" />
 *       &lt;attribute name="SubSeqMinOffset" use="required" type="{http://www.w3.org/2001/XMLSchema}integer" />
 *       &lt;attribute name="SubSeqMaxOffset" type="{http://www.w3.org/2001/XMLSchema}integer" />
 *       &lt;attribute name="MinFragLength" use="required" type="{http://www.w3.org/2001/XMLSchema}integer" />
 *     &lt;/restriction>
 *   &lt;/complexContent>
 * &lt;/complexType>
 * </pre>
 * 
 * 
 */
@XmlAccessorType(XmlAccessType.FIELD)
@XmlType(name = "SubSequenceType", propOrder = {
    "sequence",
    "defaultShift",
    "shiftOrLeftFragmentOrRightFragment"
})
public class SubSequenceType {

    @XmlElement(name = "Sequence", required = true)
    protected String sequence;
    @XmlElement(name = "DefaultShift", required = true)
    protected BigInteger defaultShift;
    @XmlElementRefs({
        @XmlElementRef(name = "Shift", namespace = "http://www.nationalarchives.gov.uk/pronom/SignatureFile", type = JAXBElement.class),
        @XmlElementRef(name = "LeftFragment", namespace = "http://www.nationalarchives.gov.uk/pronom/SignatureFile", type = JAXBElement.class),
        @XmlElementRef(name = "RightFragment", namespace = "http://www.nationalarchives.gov.uk/pronom/SignatureFile", type = JAXBElement.class)
    })
    protected List<JAXBElement<?>> shiftOrLeftFragmentOrRightFragment;
    @XmlAttribute(name = "Position", required = true)
    protected BigInteger position;
    @XmlAttribute(name = "SubSeqMinOffset", required = true)
    protected BigInteger subSeqMinOffset;
    @XmlAttribute(name = "SubSeqMaxOffset")
    protected BigInteger subSeqMaxOffset;
    @XmlAttribute(name = "MinFragLength", required = true)
    protected BigInteger minFragLength;

    /**
     * Gets the value of the sequence property.
     * 
     * @return
     *     possible object is
     *     {@link String }
     *     
     */
    public String getSequence() {
        return sequence;
    }

    /**
     * Sets the value of the sequence property.
     * 
     * @param value
     *     allowed object is
     *     {@link String }
     *     
     */
    public void setSequence(String value) {
        this.sequence = value;
    }

    /**
     * Gets the value of the defaultShift property.
     * 
     * @return
     *     possible object is
     *     {@link BigInteger }
     *     
     */
    public BigInteger getDefaultShift() {
        return defaultShift;
    }

    /**
     * Sets the value of the defaultShift property.
     * 
     * @param value
     *     allowed object is
     *     {@link BigInteger }
     *     
     */
    public void setDefaultShift(BigInteger value) {
        this.defaultShift = value;
    }

    /**
     * Gets the value of the shiftOrLeftFragmentOrRightFragment property.
     * 
     * <p>
     * This accessor method returns a reference to the live list,
     * not a snapshot. Therefore any modification you make to the
     * returned list will be present inside the JAXB object.
     * This is why there is not a <CODE>set</CODE> method for the shiftOrLeftFragmentOrRightFragment property.
     * 
     * <p>
     * For example, to add a new item, do as follows:
     * <pre>
     *    getShiftOrLeftFragmentOrRightFragment().add(newItem);
     * </pre>
     * 
     * 
     * <p>
     * Objects of the following type(s) are allowed in the list
     * {@link JAXBElement }{@code <}{@link ShiftType }{@code >}
     * {@link JAXBElement }{@code <}{@link FragmentType }{@code >}
     * {@link JAXBElement }{@code <}{@link FragmentType }{@code >}
     * 
     * 
     */
    public List<JAXBElement<?>> getShiftOrLeftFragmentOrRightFragment() {
        if (shiftOrLeftFragmentOrRightFragment == null) {
            shiftOrLeftFragmentOrRightFragment = new ArrayList<JAXBElement<?>>();
        }
        return this.shiftOrLeftFragmentOrRightFragment;
    }

    /**
     * Gets the value of the position property.
     * 
     * @return
     *     possible object is
     *     {@link BigInteger }
     *     
     */
    public BigInteger getPosition() {
        return position;
    }

    /**
     * Sets the value of the position property.
     * 
     * @param value
     *     allowed object is
     *     {@link BigInteger }
     *     
     */
    public void setPosition(BigInteger value) {
        this.position = value;
    }

    /**
     * Gets the value of the subSeqMinOffset property.
     * 
     * @return
     *     possible object is
     *     {@link BigInteger }
     *     
     */
    public BigInteger getSubSeqMinOffset() {
        return subSeqMinOffset;
    }

    /**
     * Sets the value of the subSeqMinOffset property.
     * 
     * @param value
     *     allowed object is
     *     {@link BigInteger }
     *     
     */
    public void setSubSeqMinOffset(BigInteger value) {
        this.subSeqMinOffset = value;
    }

    /**
     * Gets the value of the subSeqMaxOffset property.
     * 
     * @return
     *     possible object is
     *     {@link BigInteger }
     *     
     */
    public BigInteger getSubSeqMaxOffset() {
        return subSeqMaxOffset;
    }

    /**
     * Sets the value of the subSeqMaxOffset property.
     * 
     * @param value
     *     allowed object is
     *     {@link BigInteger }
     *     
     */
    public void setSubSeqMaxOffset(BigInteger value) {
        this.subSeqMaxOffset = value;
    }

    /**
     * Gets the value of the minFragLength property.
     * 
     * @return
     *     possible object is
     *     {@link BigInteger }
     *     
     */
    public BigInteger getMinFragLength() {
        return minFragLength;
    }

    /**
     * Sets the value of the minFragLength property.
     * 
     * @param value
     *     allowed object is
     *     {@link BigInteger }
     *     
     */
    public void setMinFragLength(BigInteger value) {
        this.minFragLength = value;
    }

}
