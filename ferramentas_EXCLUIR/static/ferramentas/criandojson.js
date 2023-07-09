
function criando_json(){
    var inputs 
    var json = "{"

    inputs = document.getElementsByClassName("ativo")
    
    var id_anterior = inputs[0].id
    for(var i = 0;i < inputs.length ;i++){
        
        
        
        
        // Entra caso o ID não esteja no JSON e o id anterior seja igual ao atual
        if(json.indexOf(inputs[i].id) == -1 && id_anterior == inputs[i].id){
            json += "\""+inputs[i].id+"\":"
            json += "{"
        }
        
        // Entra caso o ID não esteja no JSON e o id anterior seja difrente do atual
        else if(json.indexOf(inputs[i].id) == -1 && id_anterior != inputs[i].id){
            
            json += '}'
            json += ', '


            json += "\""+inputs[i].id+"\":"
            json += "{"

        }

        if(i < inputs.length){

            if(inputs[i].name == 'descricao' ){
                json += "\""+inputs[i].name+"\":\""+inputs[i].value.trim()+"\"";
            }else{
                json += "\""+inputs[i].name+"\":\""+inputs[i].value.trim()+"\"";json += ",";
            }
        }

        id_anterior = inputs[i].id


    }
    //json = json.substr(0,json.length - 1);
    json += "}";
    json += "}";
    // json = JSON.parse(json);

    document.getElementById('json').value = json


}

function nao_postar(id_anuncio){

    tags = document.getElementsByClassName(id_anuncio)
    
    for(var looping = 0; looping < tags.length; looping++){
        
        var tag_atual = tags[looping];
        var classe_da_tag = tag_atual.className
        var esta_ativo = classe_da_tag.indexOf('ativo')
        var esta_inativo = classe_da_tag.indexOf('inativo')

        if(esta_ativo != '-1' && esta_inativo == -1){
            classe_da_tag = classe_da_tag.replace('ativo', 'inativo')

            if(classe_da_tag.indexOf('btn') != -1 ){
                tag_atual.innerHTML = 'Publicar'
            }
        }
        else{
            classe_da_tag = classe_da_tag.replace('inativo', 'ativo')
            if(classe_da_tag.indexOf('btn') != -1 ){
                tag_atual.innerHTML = 'Não publicar'
            }

        }
        tag_atual.className = classe_da_tag
        
    }

}


