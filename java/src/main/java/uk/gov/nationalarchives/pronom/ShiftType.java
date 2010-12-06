
package uk.gov.nationalarchives.pronom;

import java.math.BigInteger;
import javax.xml.bind.annotation.XmlAccessType;
import javax.xml.bind.annotation.XmlAccessorType;
import javax.xml.bind.annotation.XmlAttribute;
import javax.xml.bind.annotation.XmlType;
import javax.xml.bind.annotation.XmlValue;


/**
 * <p>Java class for ShiftType complex type.
 * 
 * <p>The following schema fragment specifies the expected content contained within this class.
 * 
 * <pre>
 * &lt;complexType name="ShiftType">
 *   &lt;simpleContent>
 *     &lt;extension base="&lt;http://www.w3.org/2001/XMLSchema>integer">
 *       &lt;attribute name="Byte" type="{http://www.nationalarchives.gov.uk/pronom/SignatureFile}HexByte" />
 *     &lt;/extension>
 *   &lt;/simpleContent>
 * &lt;/complexType>
 * </pre>
 * 
 * 
 */
@XmlAccessorType(XmlAccessType.FIELD)
@XmlType(name = "ShiftType", propOrder = {
    "value"
})
public class ShiftType {

    @XmlValue
    protected BigInteger value;
    @XmlAttribute(name = "Byte")
    protected String _byte;

    /**
     * Gets the value of the value property.
     * 
     * @return
     *     possible object is
     *     {@link BigInteger }
     *     
     */
    public BigInteger getValue() {
        return value;
    }

    /**
     * Sets the value of the value property.
     * 
     * @param value
     *     allowed object is
     *     {@link BigInteger }
     *     
     */
    public void setValue(BigInteger value) {
        this.value = value;
    }

    /**
     * Gets the value of the byte property.
     * 
     * @return
     *     possible object is
     *     {@link String }
     *     
     */
    public String getByte() {
        return _byte;
    }

    /**
     * Sets the value of the byte property.
     * 
     * @param value
     *     allowed object is
     *     {@link String }
     *     
     */
    public void setByte(String value) {
        this._byte = value;
    }

}
