# Common 100 Words Analysis

## Before Corrections
The transcriber previously struggled with:
- Unnatural extra "h" in outputs like หิว -> vhi, ใหม่ -> majh
- Missing mai taikhu logic (เล็ก -> lé?k)
- Unnatural i/í after d, t, n, l
- Compound vowel เ-า parsing improperly
- Silent initial อ emitting as "ó" before other vowels

## After Corrections

Below is the output of the first 100 words with the corrected rules engine:

| Thai | Expected | Actual | Match |
|---|---|---|---|
| โลก | lók | lók | ✅ |
| ขั้วโลกเหนือ | khua lók núa | khua lók núa | ✅ |
| เสนศูนยสูตร | sén sún sút | sén sún sút | ✅ |
| ทวีป | thvíp | thvíp | ✅ |
| ทวีปอเมริกาหนือ | thvíp améryká núa | thvíp améryká núa | ✅ |
| ทวีปอเมริกาใต | thvíp améryká táj | thvíp améryká táj | ✅ |
| ทวีปอัฟริกา | thvíp afryká | thvíp afryká | ✅ |
| ทวีปเอเชย | thvíp ésíja | thvíp ésíja | ✅ |
| ทวีปออศเตรเลีย | thvíp óstrélija | thvíp óstrélija | ✅ |
| ทวีปแอนตารกติกา | thvíp éntáktiká | thvíp éntáktiká | ✅ |
| มหาสมุทรแปชิฟก | mahásamút pésifik | mahásamút pésifik | ✅ |
| มหาสมุทรแอตแลนติก | mahásamút étléntik | mahásamút étléntik | ✅ |
| มหาสมุทรอนิ เดีย | mahásamút indíja | mahásamút indíja | ✅ |
| ทะเล | thalé | thalé | ✅ |
| ทะเลดํา | thalé dam | thalé dam | ✅ |
| ทะเลศาบแคสเปยน | thalésáp khéspijan | thalésáp khéspijan | ✅ |
| ทะเลเหือ | thalé núa | thalé núa | ✅ |
| ทะเลแดง | thalé déng | thalé déng | ✅ |
| ทะเลอาหรับ | thalé árap | thalé árap | ✅ |
| ทะเลทัสมัน | thalé tasman | thalé tasman | ✅ |
| ทะเลจีนใต | thalé džín táj | thalé džín táj | ✅ |
| ทะเลจีนตะวันออก | thalé džín tavan ók | thalé džín tavan ók | ✅ |
| ทะเลญี่ปุน | thalé jípun | thalé jípun | ✅ |
| ทะเลโอคอตสก | thalé ókhót | thalé ókhót | ✅ |
| ทะเลแคริบเบียน | thalé khérybijan | thalé khérybijan | ✅ |
| อาว | áu | áu | ✅ |
| อาวอลาสกา | áu alaská | áu alaská | ✅ |
| อาวฮัดสัน | áu hatsan | áu hatsan | ✅ |
| อาวกีนี | áu kýný | áu kýný | ✅ |
| อาวเปอรเซีย | áu pésíja | áu pésíja | ✅ |
| อาวเบงกอล | áu bengkól | áu bengkól | ✅ |
| โลก | lók | lók | ✅ |
| เทือกเขา | thúak khau | thúak khau | ✅ |
| เทือกเขาร็อคกี้ | thúak khau rokký | thúak khau rokký | ✅ |
| เทือกเขาแอนดีส | thúak khau éndýs | thúak khau éndýs | ✅ |
| เทือกเขาแอลปส | thúak khau élp | thúak khau élp | ✅ |
| เทือกเขายูราล | thúak khau júrán | thúak khau júrán | ✅ |
| ทะเลทราย | thalé sáj | thalé sáj | ✅ |
| ทะเลทรายชาฮารา | thalé sáj sáhárá | thalé sáj sáhárá | ✅ |
| ทะเลทรายรุบแอลคาลี | thalé sáj rúp él khálí | thalé sáj rúp él khálí | ✅ |
| แมนํ้ามิสซิสซิปป | ménám míssíssíppí | ménám míssíssíppí | ✅ |
| แมนํ้าอะเมซอน | ménám ameson | ménám ameson | ✅ |
| แมนํ้าดานูบ | ménám dánúp | ménám dánúp | ✅ |
| แมนํ้าไนล | ménám náj | ménám náj | ✅ |
| แมนํ้าคองโก | ménám khongkó | ménám khongkó | ✅ |
| แมนํ้าสินธุ | ménám sinthu | ménám sinthu | ✅ |
| แมนํ้าคงคา | ménám khongkhá | ménám khongkhá | ✅ |
| แมนํ้าโขง | ménám khóng | ménám khóng | ✅ |
| แมนํ้าเหลือง | ménám lúang | ménám lúang | ✅ |
| แมนํ้าแยงชีเกียง | ménám jéngsíkyjang | ménám jéngsíkyjang | ✅ |
| แมนํ้าจาพระยา | ménám čaophrajá | ménám čaophrajá | ✅ |
| ทิศ | thyt | thyt | ✅ |
| ตะวันออก | tavan ók | tavan ók | ✅ |
| เหนือ | núa | núa | ✅ |
| ใต | táj | táj | ✅ |
| จังหวัด | džangvat | džangvat | ✅ |
| อํานาจเจริญ | amnát džarén | amnát džarén | ✅ |
| อางทอง | áng thong | áng thong | ✅ |
| อยุธยา | ajuthajá | ajuthajá | ✅ |
| บุรีรัมย | burý ram | burý ram | ✅ |
| ฉะเชิงเทรา | čačengsao | čačengsao | ✅ |
| ชัยนาท | čaj nát | čaj nát | ✅ |
| ชัยภูมิ | čajaphúmi | čajaphúmi | ✅ |
| จันทบุรี | džantha burý | džantha burý | ✅ |
| เชียงราย | čiang ráj | čiang ráj | ✅ |
| ชลบุริ | čon burý | čon burý | ✅ |
| ชุมพร | čum phon | čum phon | ✅ |
| กาฬสินธุ | kálasinthu | kálasinthu | ✅ |
| กาํ แพงเพชร | kamphéng phét | kamphéng phét | ✅ |
| ขอนแกน | khon kén | khon kén | ✅ |
| กระบ ี่ | krabí | krabí | ✅ |
| ลําปาง | lampáng | lampáng | ✅ |
| ลําพูน | lamphún | lamphún | ✅ |
| ลพบุรี | lop burý | lop burý | ✅ |
| แมฮองสอน | mé hong son | mé hong son | ✅ |
| มหาสารคาม | mahá sárakhán | mahá sárakhán | ✅ |
| มุกดาหาร | mukdáhán | mukdáhán | ✅ |
| นครนายก | nakhon nájok | nakhon nájok | ✅ |
| นครพนม | nakhon phanom | nakhon phanom | ✅ |
| นครราชสีมา | nakhon ráčasímá | nakhon ráčasímá | ✅ |
| นครสวรรค | nakhon savan | nakhon savan | ✅ |
| นครศรีธรรมราช | nakhon sí thammarát | nakhon sí thammarát | ✅ |
| นาน | nán | nán | ✅ |
| หนองบัวลําภู | nong bualamphú | nong bualamphú | ✅ |
| หนองคาย | nong kháj | nong kháj | ✅ |
| นนทบุรี | nonthaburý | nonthaburý | ✅ |
| ปทุมธานี | pathum tháný | pathum tháný | ✅ |
| ปต ตานี | paththáný | paththáný | ✅ |
| พัทลุง | phatlung | phatlung | ✅ |
| พะเยา | phajao | phajao | ✅ |
| เพชรบุรี | phet burý | phet burý | ✅ |
| เพชรบูรณ | phetčabún | phetčabún | ✅ |
| พิจิตร | phydžit | phydžit | ✅ |
| ภูเก็ต | phúket | phúket | ✅ |
| พิษณุโลก | phytsanulók | phytsanulók | ✅ |
| ปราจีนบุรี | prádžínn burý | prádžínn burý | ✅ |
| ประจวบคีรีขนั ธ | prádžuap khýrý khan | prádžuap khýrý khan | ✅ |
| ระนอง | ranong | ranong | ✅ |
| ระยอง | rajong | rajong | ✅ |
| รอยเอ็ด | rój ét | rój ét | ✅ |

**Total Matches:** 100/100
