
package uk.gov.nationalarchives.pronom;

import java.io.Serializable;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;
import javax.xml.bind.JAXBElement;
import javax.xml.bind.annotation.XmlAccessType;
import javax.xml.bind.annotation.XmlAccessorType;
import javax.xml.bind.annotation.XmlAttribute;
import javax.xml.bind.annotation.XmlElementRef;
import javax.xml.bind.annotation.XmlElementRefs;
import javax.xml.bind.annotation.XmlSchemaType;
import javax.xml.bind.annotation.XmlType;


/**
 * <p>Java class for FileFormatType complex type.
 * 
 * <p>The following schema fragment specifies the expected content contained within this class.
 * 
 * <pre>
 * &lt;complexType name="FileFormatType">
 *   &lt;complexContent>
 *     &lt;restriction base="{http://www.w3.org/2001/XMLSchema}anyType">
 *       &lt;choice maxOccurs="unbounded" minOccurs="0">
 *         &lt;element name="InternalSignatureID" type="{http://www.w3.org/2001/XMLSchema}nonNegativeInteger"/>
 *         &lt;element name="Extension" type="{http://www.nationalarchives.gov.uk/pronom/SignatureFile}NonEmptyString"/>
 *         &lt;element name="HasPriorityOverFileFormatID" type="{http://www.w3.org/2001/XMLSchema}nonNegativeInteger"/>
 *       &lt;/choice>
 *       &lt;attribute name="ID" use="required" type="{http://www.w3.org/2001/XMLSchema}nonNegativeInteger" />
 *       &lt;attribute name="Name" use="required" type="{http://www.nationalarchives.gov.uk/pronom/SignatureFile}String100" />
 *       &lt;attribute name="Version" type="{http://www.nationalarchives.gov.uk/pronom/SignatureFile}String50" />
 *       &lt;attribute name="PUID" type="{http://www.nationalarchives.gov.uk/pronom/SignatureFile}String150" />
 *       &lt;attribute name="MIMEType" type="{http://www.nationalarchives.gov.uk/pronom/SignatureFile}String150" />
 *     &lt;/restriction>
 *   &lt;/complexContent>
 * &lt;/complexType>
 * </pre>
 * 
 * 
 */
@XmlAccessorType(XmlAccessType.FIELD)
@XmlType(name = "FileFormatType", propOrder = {
    "internalSignatureIDOrExtensionOrHasPriorityOverFileFormatID"
})
public class FileFormatType {

    @XmlElementRefs({
        @XmlElementRef(name = "InternalSignatureID", namespace = "http://www.nationalarchives.gov.uk/pronom/SignatureFile", type = JAXBElement.class),
        @XmlElementRef(name = "HasPriorityOverFileFormatID", namespace = "http://www.nationalarchives.gov.uk/pronom/SignatureFile", type = JAXBElement.class),
        @XmlElementRef(name = "Extension", namespace = "http://www.nationalarchives.gov.uk/pronom/SignatureFile", type = JAXBElement.class)
    })
    protected List<JAXBElement<? extends Serializable>> internalSignatureIDOrExtensionOrHasPriorityOverFileFormatID;
    @XmlAttribute(name = "ID", required = true)
    @XmlSchemaType(name = "nonNegativeInteger")
    protected BigInteger id;
    @XmlAttribute(name = "Name", required = true)
    protected String name;
    @XmlAttribute(name = "Version")
    protected String version;
    @XmlAttribute(name = "PUID")
    protected String puid;
    @XmlAttribute(name = "MIMEType")
    protected String mimeType;

    /**
     * Gets the value of the internalSignatureIDOrExtensionOrHasPriorityOverFileFormatID property.
     * 
     * <p>
     * This accessor method returns a reference to the live list,
     * not a snapshot. Therefore any modification you make to the
     * returned list will be present inside the JAXB object.
     * This is why there is not a <CODE>set</CODE> method for the internalSignatureIDOrExtensionOrHasPriorityOverFileFormatID property.
     * 
     * <p>
     * For example, to add a new item, do as follows:
     * <pre>
     *    getInternalSignatureIDOrExtensionOrHasPriorityOverFileFormatID().add(newItem);
     * </pre>
     * 
     * 
     * <p>
     * Objects of the following type(s) are allowed in the list
     * {@link JAXBElement }{@code <}{@link String }{@code >}
     * {@link JAXBElement }{@code <}{@link BigInteger }{@code >}
     * {@link JAXBElement }{@code <}{@link BigInteger }{@code >}
     * 
     * 
     */
    public List<JAXBElement<? extends Serializable>> getInternalSignatureIDOrExtensionOrHasPriorityOverFileFormatID() {
        if (internalSignatureIDOrExtensionOrHasPriorityOverFileFormatID == null) {
            internalSignatureIDOrExtensionOrHasPriorityOverFileFormatID = new ArrayList<JAXBElement<? extends Serializable>>();
        }
        return this.internalSignatureIDOrExtensionOrHasPriorityOverFileFormatID;
    }

    /**
     * Gets the value of the id property.
     * 
     * @return
     *     possible object is
     *     {@link BigInteger }
     *     
     */
    public BigInteger getID() {
        return id;
    }

    /**
     * Sets the value of the id property.
     * 
     * @param value
     *     allowed object is
     *     {@link BigInteger }
     *     
     */
    public void setID(BigInteger value) {
        this.id = value;
    }

    /**
     * Gets the value of the name property.
     * 
     * @return
     *     possible object is
     *     {@link String }
     *     
     */
    public String getName() {
        return name;
    }

    /**
     * Sets the value of the name property.
     * 
     * @param value
     *     allowed object is
     *     {@link String }
     *     
     */
    public void setName(String value) {
        this.name = value;
    }

    /**
     * Gets the value of the version property.
     * 
     * @return
     *     possible object is
     *     {@link String }
     *     
     */
    public String getVersion() {
        return version;
    }

    /**
     * Sets the value of the version property.
     * 
     * @param value
     *     allowed object is
     *     {@link String }
     *     
     */
    public void setVersion(String value) {
        this.version = value;
    }

    /**
     * Gets the value of the puid property.
     * 
     * @return
     *     possible object is
     *     {@link String }
     *     
     */
    public String getPUID() {
        return puid;
    }

    /**
     * Sets the value of the puid property.
     * 
     * @param value
     *     allowed object is
     *     {@link String }
     *     
     */
    public void setPUID(String value) {
        this.puid = value;
    }

    /**
     * Gets the value of the mimeType property.
     * 
     * @return
     *     possible object is
     *     {@link String }
     *     
     */
    public String getMIMEType() {
        return mimeType;
    }

    /**
     * Sets the value of the mimeType property.
     * 
     * @param value
     *     allowed object is
     *     {@link String }
     *     
     */
    public void setMIMEType(String value) {
        this.mimeType = value;
    }

}
