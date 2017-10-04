

local content_encoding = ngx.req.get_headers()["Content-Encoding"]
-- ngx.log(ngx.ERR, string.format("Content-Encoding: %s", tostring(content_encoding)))

if content_encoding == "gzip" then

    local codes = {}
    codes[4001] = "Corrupted GZIP body"
    codes[4002] = "Invalid GZIP body"
    codes[4003] = "Uncompressed body too large"
    codes[5001] = "The in-file request body data isn't readable"
    codes[5002] = "Unable to create a temporary file"

    ngx.ctx.max_chunk_size = tonumber(ngx.var.max_chunk_size)
    ngx.ctx.max_body_size = tonumber(ngx.var.max_body_size)

    Gunzipper = {}
    Gunzipper.codes = codes
    Gunzipper.__index = Gunzipper

    function Gunzipper:new()
        ngx.req.read_body()

        local data = ngx.req.get_body_data()
        local file_name = ngx.req.get_body_file()
        if data ~= nil or file_name ~= nil then
            local properties = {
                data = data,
                file_name = file_name,
                stream = require("zlib").inflate()
            }
            setmetatable(properties, Gunzipper)
            return properties
        end
        return nil
    end


    function Gunzipper:unzip_body()
        ngx.req.clear_header("Content-Encoding")
        ngx.req.clear_header("Content-Length")
        if self.data ~= nil then
            -- ngx.log(ngx.ERR, string.format("Data lenght: %d", self.data:len()))
            local new_data = self:inflate_body(self.data)
            ngx.req.set_body_data(new_data)
        else
            -- ngx.log(ngx.ERR, string.format("File name: %s", self.file_name))
            local new_body_file = self:inflate_file(self.file_name)
            ngx.req.set_body_file(new_body_file, true)
        end
    end


    function Gunzipper:create_error_response(code)
        local message = 'Unknown error';
        if code > 4000 and code < 5000 then
            ngx.status = ngx.HTTP_BAD_REQUEST
            message = string.format('{ \n' ..
                    '   "status": 400, \n' ..
                    '   "statusReason": "Bad Request", \n' ..
                    '   "code": %d, \n' ..
                    '   "description": "%s", \n' ..
                    '   "message": "HTTP 400 Bad Request" \n' ..
                    '}', code, self.codes[code])
        elseif code > 5000 and code < 6000 then
            ngx.status = ngx.HTTP_INTERNAL_SERVER_ERROR
            message = string.format('{ \n' ..
                    '   "status": 500, \n' ..
                    '   "statusReason": "Internal Server Error", \n' ..
                    '   "code": %d, \n' ..
                    '   "description": "%s", \n' ..
                    '   "message": "HTTP 500 Internal Server Error" \n' ..
                    '}', code, self.codes[code])
        else
            ngx.status = gx.HTTP_INTERNAL_SERVER_ERROR
        end
        ngx.header.content_type = "application/json"
        -- ngx.log(ngx.ERR, message)
        ngx.say(message)
        ngx.exit(ngx.HTTP_OK)
    end


    function Gunzipper:inflate(chunk)
        local status, output, eof, bytes_in, bytes_out = pcall(self.stream, chunk)
        if not status then
            -- corrupted chunk
            error({code=4001})
        end

        if bytes_in == 0 and bytes_out == 0 then
            -- body is not gzip compressed
            serror({code=4002})
        end

        if bytes_out > ngx.ctx.max_body_size then
            -- uncompressed body too large
            error({code=4003})
        end

        -- ngx.log(ngx.ERR, bytes_out)
        return output
    end


    function Gunzipper:inflate_body(data)
        local chunk = ""
        local buffer = {}

        for index = 0, data:len(), ngx.ctx.max_chunk_size do
            chunk = string.sub(data, index, index + ngx.ctx.max_chunk_size - 1)
            local status, output = pcall(Gunzipper.inflate, self, chunk)
            if not status then
                self:create_error_response(output.code)
            end
            table.insert(buffer, output)
        end

        return table.concat(buffer)
    end


    function Gunzipper:open(file_name, mode, error_code)
        local fl, error, ret = io.open(file_name, mode)
        if fl == nil then
            ngx.log(ngx.ERR, self.codes[error_code] .. ". " .. error)
            self:create_error_response(error_code)
        end
        return fl
    end


    function Gunzipper:inflate_file(file_name)
        local chunk = ""
        local new_file_name = file_name .. '.unzipped'

        local out_fl = self:open(new_file_name, 'wb', 5002)
        local in_fl =  self:open(file_name, 'rb', 5001)

        while true do
            chunk = in_fl:read(ngx.ctx.max_chunk_size)
            if not chunk then break end
            local status, output = pcall(Gunzipper.inflate, self, chunk)
            if not status then
                in_fl:close()
                out_fl:close()
                os.remove(new_file_name)
                self:create_error_response(output.code)
            end
            out_fl:write(output)
        end
        in_fl:close()
        out_fl:close()
        return new_file_name
    end


    -- Process gzipped request
    local unzipper = Gunzipper:new()
    if unzipper ~= nil then
        -- ngx.log(ngx.ERR, "Gunzipper is working")
        unzipper:unzip_body()
    end

end
