// ============================================================
// UNS VISA SYSTEM - VALIDACIONES
// Validadores para datos de visa japonesa
// ============================================================

const VisaValidators = {
    
    // ============================================================
    // 在留カード番号 (Residence Card Number)
    // Formato: 2 letras + 8 números + 2 letras
    // Ejemplo: AB12345678CD
    // ============================================================
    residenceCard: {
        pattern: /^[A-Z]{2}\d{8}[A-Z]{2}$/,
        
        validate(value) {
            if (!value) return { valid: false, error: '在留カード番号を入力してください' };
            
            const clean = value.toUpperCase().replace(/\s/g, '');
            
            if (!this.pattern.test(clean)) {
                return {
                    valid: false,
                    error: '形式が無効です（例：AB12345678CD）',
                    hint: '2文字 + 8桁数字 + 2文字'
                };
            }
            
            return { valid: true, formatted: clean };
        },
        
        format(value) {
            if (!value) return '';
            return value.toUpperCase().replace(/\s/g, '');
        }
    },

    // ============================================================
    // 法人番号 (Corporation Number)
    // Formato: 13 dígitos
    // ============================================================
    corporationNumber: {
        pattern: /^\d{13}$/,
        
        validate(value) {
            if (!value) return { valid: true }; // Opcional
            
            const clean = value.replace(/\s/g, '');
            
            if (!this.pattern.test(clean)) {
                return {
                    valid: false,
                    error: '法人番号は13桁の数字です',
                    hint: '国税庁法人番号公表サイトで確認できます'
                };
            }
            
            // Validación de checksum (opcional pero recomendada)
            if (!this.validateChecksum(clean)) {
                return {
                    valid: false,
                    error: '法人番号のチェックサムが無効です',
                    hint: '番号を再確認してください'
                };
            }
            
            return { valid: true, formatted: clean };
        },
        
        validateChecksum(number) {
            // El primer dígito es el check digit
            const digits = number.split('').map(Number);
            const checkDigit = digits[0];
            const body = digits.slice(1);
            
            // Cálculo del check digit
            let sum = 0;
            for (let i = 0; i < body.length; i++) {
                const weight = (i % 2 === 0) ? 1 : 2;
                sum += body[i] * weight;
            }
            
            const calculated = (9 - (sum % 9)) % 9;
            return checkDigit === calculated;
        },
        
        format(value) {
            if (!value) return '';
            return value.replace(/\s/g, '');
        }
    },

    // ============================================================
    // 雇用保険適用事業所番号 (Employment Insurance Number)
    // Formato: 11 dígitos (4桁-6桁-1桁)
    // ============================================================
    employmentInsuranceNumber: {
        pattern: /^\d{11}$/,
        
        validate(value) {
            if (!value) return { valid: true }; // Opcional
            
            const clean = value.replace(/[-\s]/g, '');
            
            if (!this.pattern.test(clean)) {
                return {
                    valid: false,
                    error: '雇用保険番号は11桁の数字です',
                    hint: '形式: XXXX-XXXXXX-X'
                };
            }
            
            return { valid: true, formatted: this.format(clean) };
        },
        
        format(value) {
            if (!value) return '';
            const clean = value.replace(/[-\s]/g, '');
            if (clean.length === 11) {
                return `${clean.slice(0,4)}-${clean.slice(4,10)}-${clean.slice(10)}`;
            }
            return clean;
        }
    },

    // ============================================================
    // パスポート番号 (Passport Number)
    // Formatos varían por nacionalidad
    // ============================================================
    passportNumber: {
        patterns: {
            'ベトナム': /^[A-Z]\d{7,8}$/,
            'VIETNAM': /^[A-Z]\d{7,8}$/,
            '中国': /^[A-Z]\d{8}$/,
            'CHINA': /^[A-Z]\d{8}$/,
            'フィリピン': /^[A-Z]{2}\d{7}$/,
            'PHILIPPINES': /^[A-Z]{2}\d{7}$/,
            'インドネシア': /^[A-Z]\d{7}$/,
            'INDONESIA': /^[A-Z]\d{7}$/,
            'ネパール': /^\d{8}$/,
            'NEPAL': /^\d{8}$/,
            'ブラジル': /^[A-Z]{2}\d{6}$/,
            'BRAZIL': /^[A-Z]{2}\d{6}$/,
            '韓国': /^[A-Z]\d{8}$/,
            'KOREA': /^[A-Z]\d{8}$/,
            'default': /^[A-Z0-9]{6,9}$/
        },
        
        validate(value, nationality = 'default') {
            if (!value) return { valid: false, error: '旅券番号を入力してください' };
            
            const clean = value.toUpperCase().replace(/\s/g, '');
            const pattern = this.patterns[nationality] || this.patterns['default'];
            
            if (!pattern.test(clean)) {
                return {
                    valid: false,
                    error: '旅券番号の形式が無効です',
                    hint: `${nationality}のパスポート形式を確認してください`
                };
            }
            
            return { valid: true, formatted: clean };
        },
        
        format(value) {
            return value ? value.toUpperCase().replace(/\s/g, '') : '';
        }
    },

    // ============================================================
    // 電話番号 (Japanese Phone Number)
    // Formatos: 固定電話 0X-XXXX-XXXX, 携帯 0X0-XXXX-XXXX
    // ============================================================
    phoneNumber: {
        patterns: {
            landline: /^0\d{1,4}-?\d{1,4}-?\d{4}$/,
            mobile: /^0[789]0-?\d{4}-?\d{4}$/
        },
        
        validate(value, type = 'any') {
            if (!value) return { valid: true }; // Opcional
            
            const clean = value.replace(/[-\s]/g, '');
            
            if (type === 'mobile') {
                if (!this.patterns.mobile.test(value.replace(/\s/g, ''))) {
                    return {
                        valid: false,
                        error: '携帯電話番号の形式が無効です',
                        hint: '例: 090-1234-5678'
                    };
                }
            } else if (type === 'landline') {
                if (!this.patterns.landline.test(value.replace(/\s/g, ''))) {
                    return {
                        valid: false,
                        error: '固定電話番号の形式が無効です',
                        hint: '例: 052-123-4567'
                    };
                }
            } else {
                // Any phone
                if (!/^0\d{9,10}$/.test(clean)) {
                    return {
                        valid: false,
                        error: '電話番号の形式が無効です',
                        hint: '例: 052-123-4567 または 090-1234-5678'
                    };
                }
            }
            
            return { valid: true, formatted: this.format(clean) };
        },
        
        format(value) {
            if (!value) return '';
            const clean = value.replace(/[-\s]/g, '');
            
            // Móvil (11 dígitos empezando con 070/080/090)
            if (/^0[789]0\d{8}$/.test(clean)) {
                return `${clean.slice(0,3)}-${clean.slice(3,7)}-${clean.slice(7)}`;
            }
            
            // Fijo (10 dígitos)
            if (/^0\d{9}$/.test(clean)) {
                // Detectar área
                if (clean.startsWith('03') || clean.startsWith('06')) {
                    // Tokyo/Osaka: 03-XXXX-XXXX
                    return `${clean.slice(0,2)}-${clean.slice(2,6)}-${clean.slice(6)}`;
                } else {
                    // Otras áreas: 0XX-XXX-XXXX
                    return `${clean.slice(0,3)}-${clean.slice(3,6)}-${clean.slice(6)}`;
                }
            }
            
            return clean;
        }
    },

    // ============================================================
    // 郵便番号 (Postal Code)
    // Formato: XXX-XXXX
    // ============================================================
    postalCode: {
        pattern: /^\d{7}$/,
        
        validate(value) {
            if (!value) return { valid: true }; // Opcional
            
            const clean = value.replace(/[-\s]/g, '');
            
            if (!this.pattern.test(clean)) {
                return {
                    valid: false,
                    error: '郵便番号は7桁の数字です',
                    hint: '例: 123-4567'
                };
            }
            
            return { valid: true, formatted: this.format(clean) };
        },
        
        format(value) {
            if (!value) return '';
            const clean = value.replace(/[-\s]/g, '');
            return clean.length === 7 ? `${clean.slice(0,3)}-${clean.slice(3)}` : clean;
        }
    },

    // ============================================================
    // 在留期限 (Visa Expiration)
    // Calcula estado y días restantes
    // ============================================================
    visaExpiration: {
        validate(expirationDate) {
            if (!expirationDate) {
                return { valid: false, error: '在留期限を入力してください' };
            }
            
            const expDate = new Date(expirationDate);
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            
            const diffTime = expDate - today;
            const daysRemaining = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            let status, urgency, message, canRenew;
            
            if (daysRemaining < 0) {
                status = 'expired';
                urgency = 'error';
                message = `期限切れ（${Math.abs(daysRemaining)}日経過）`;
                canRenew = false;
            } else if (daysRemaining === 0) {
                status = 'expiring_today';
                urgency = 'error';
                message = '本日期限切れ';
                canRenew = true;
            } else if (daysRemaining <= 30) {
                status = 'critical';
                urgency = 'error';
                message = `期限まで${daysRemaining}日（緊急）`;
                canRenew = true;
            } else if (daysRemaining <= 60) {
                status = 'warning';
                urgency = 'warning';
                message = `期限まで${daysRemaining}日（要注意）`;
                canRenew = true;
            } else if (daysRemaining <= 90) {
                status = 'soon';
                urgency = 'info';
                message = `期限まで${daysRemaining}日（更新可能）`;
                canRenew = true;
            } else {
                status = 'ok';
                urgency = 'success';
                message = `期限まで${daysRemaining}日`;
                canRenew = false;
            }
            
            return {
                valid: true,
                daysRemaining,
                status,
                urgency,
                message,
                canRenew,
                expirationDate: expDate.toISOString().split('T')[0]
            };
        }
    },

    // ============================================================
    // 日付 (Date Validation)
    // ============================================================
    date: {
        validate(value, options = {}) {
            const { 
                required = false, 
                minDate = null, 
                maxDate = null,
                label = '日付'
            } = options;
            
            if (!value) {
                return required 
                    ? { valid: false, error: `${label}を入力してください` }
                    : { valid: true };
            }
            
            const date = new Date(value);
            if (isNaN(date.getTime())) {
                return { valid: false, error: `${label}の形式が無効です` };
            }
            
            if (minDate && date < new Date(minDate)) {
                return { valid: false, error: `${label}は${minDate}以降である必要があります` };
            }
            
            if (maxDate && date > new Date(maxDate)) {
                return { valid: false, error: `${label}は${maxDate}以前である必要があります` };
            }
            
            return { valid: true, formatted: date.toISOString().split('T')[0] };
        },
        
        // Validar fecha de nacimiento (debe ser mayor de 18 años)
        validateBirthDate(value) {
            const result = this.validate(value, { required: true, label: '生年月日' });
            if (!result.valid) return result;
            
            const birthDate = new Date(value);
            const today = new Date();
            let age = today.getFullYear() - birthDate.getFullYear();
            const m = today.getMonth() - birthDate.getMonth();
            if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
                age--;
            }
            
            if (age < 18) {
                return { valid: false, error: '申請者は18歳以上である必要があります' };
            }
            
            return { ...result, age };
        }
    },

    // ============================================================
    // メールアドレス (Email)
    // ============================================================
    email: {
        pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        
        validate(value) {
            if (!value) return { valid: true }; // Opcional
            
            if (!this.pattern.test(value)) {
                return {
                    valid: false,
                    error: 'メールアドレスの形式が無効です',
                    hint: '例: example@domain.com'
                };
            }
            
            return { valid: true, formatted: value.toLowerCase() };
        }
    },

    // ============================================================
    // 氏名 (Name)
    // ============================================================
    name: {
        validateRomaji(value, options = {}) {
            const { required = true, label = '氏名' } = options;
            
            if (!value) {
                return required 
                    ? { valid: false, error: `${label}を入力してください` }
                    : { valid: true };
            }
            
            // Solo letras del alfabeto y espacios
            if (!/^[A-Za-z\s]+$/.test(value)) {
                return {
                    valid: false,
                    error: `${label}はローマ字で入力してください`,
                    hint: '漢字やひらがなは使用できません'
                };
            }
            
            return { valid: true, formatted: value.toUpperCase() };
        },
        
        validateKanji(value) {
            if (!value) return { valid: true }; // Opcional
            
            // Permitir kanji, hiragana, katakana
            if (!/^[\u4e00-\u9faf\u3040-\u309f\u30a0-\u30ff\s]+$/.test(value)) {
                return {
                    valid: false,
                    error: '漢字、ひらがな、カタカナで入力してください'
                };
            }
            
            return { valid: true };
        }
    },

    // ============================================================
    // Validar formulario completo
    // ============================================================
    validateForm(formData) {
        const errors = {};
        const warnings = [];
        
        // Nombre
        const familyNameResult = this.name.validateRomaji(formData.familyName, { label: '姓' });
        if (!familyNameResult.valid) errors.familyName = familyNameResult.error;
        
        const givenNameResult = this.name.validateRomaji(formData.givenName, { label: '名' });
        if (!givenNameResult.valid) errors.givenName = givenNameResult.error;
        
        // 在留カード
        if (formData.residenceCardNumber) {
            const cardResult = this.residenceCard.validate(formData.residenceCardNumber);
            if (!cardResult.valid) errors.residenceCardNumber = cardResult.error;
        }
        
        // パスポート
        const passportResult = this.passportNumber.validate(formData.passportNumber, formData.nationality);
        if (!passportResult.valid) errors.passportNumber = passportResult.error;
        
        // 在留期限
        if (formData.currentExpirationDate) {
            const expResult = this.visaExpiration.validate(formData.currentExpirationDate);
            if (!expResult.valid) {
                errors.currentExpirationDate = expResult.error;
            } else if (expResult.urgency === 'error') {
                warnings.push(expResult.message);
            }
        }
        
        // パスポート期限
        if (formData.passportExpiration) {
            const passExpResult = this.visaExpiration.validate(formData.passportExpiration);
            if (passExpResult.status === 'expired') {
                errors.passportExpiration = 'パスポートの期限が切れています';
            }
        }
        
        // 電話番号
        if (formData.telephoneJapan) {
            const phoneResult = this.phoneNumber.validate(formData.telephoneJapan, 'landline');
            if (!phoneResult.valid) errors.telephoneJapan = phoneResult.error;
        }
        
        if (formData.cellularPhone) {
            const mobileResult = this.phoneNumber.validate(formData.cellularPhone, 'mobile');
            if (!mobileResult.valid) errors.cellularPhone = mobileResult.error;
        }
        
        // メール
        if (formData.email) {
            const emailResult = this.email.validate(formData.email);
            if (!emailResult.valid) errors.email = emailResult.error;
        }
        
        // 郵便番号
        if (formData.postalCodeJapan) {
            const postalResult = this.postalCode.validate(formData.postalCodeJapan);
            if (!postalResult.valid) errors.postalCodeJapan = postalResult.error;
        }
        
        // 生年月日
        if (formData.dateOfBirth) {
            const birthResult = this.date.validateBirthDate(formData.dateOfBirth);
            if (!birthResult.valid) errors.dateOfBirth = birthResult.error;
        }
        
        return {
            isValid: Object.keys(errors).length === 0,
            errors,
            warnings,
            errorCount: Object.keys(errors).length,
            warningCount: warnings.length
        };
    }
};

// Exportar para uso en módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VisaValidators;
}
